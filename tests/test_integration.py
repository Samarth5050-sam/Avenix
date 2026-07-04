# Integration tests for Avenix tracing

import io
import time
import types
from unittest import mock

import pytest
from rich.console import Console

from avenix import trace, Tracer
from avenix.logger import RichLogger


class TestEndToEndDecorator:
    """Task 8.2: End-to-end decorator test."""

    def test_trace_decorator_captures_and_displays(self):
        """Decorate a function returning a mock OpenAI response, verify output."""
        # Create a mock OpenAI response
        usage = types.SimpleNamespace(
            prompt_tokens=150,
            completion_tokens=300,
        )
        message = types.SimpleNamespace(
            content='Hello! How can I help you today?',
        )
        choice = types.SimpleNamespace(message=message)
        mock_response = types.SimpleNamespace(
            model='gpt-4',
            usage=usage,
            choices=[choice],
        )

        # Decorate a function that returns the mock response
        @trace
        def call_openai(prompt: str):
            return mock_response

        # Capture the trace output via StringIO
        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)
        rich_logger = RichLogger(console=console)

        # Patch the tracer's logger to use our capturing console
        with mock.patch.object(
            call_openai, '__wrapped__', side_effect=None
        ) if False else _patch_tracer_logger(call_openai, rich_logger):
            result = call_openai('Hello')

        # Verify the function returns the correct value
        assert result is mock_response
        assert result.model == 'gpt-4'
        assert result.usage.prompt_tokens == 150
        assert result.usage.completion_tokens == 300
        assert result.choices[0].message.content == 'Hello! How can I help you today?'

        # Verify the trace output contains expected information
        output = string_io.getvalue()
        assert 'gpt-4' in output
        assert '150' in output
        assert '300' in output

    def test_trace_decorator_returns_original_result(self):
        """Verify the decorated function returns its original result unchanged."""
        usage = types.SimpleNamespace(prompt_tokens=10, completion_tokens=20)
        message = types.SimpleNamespace(content='Test response')
        choice = types.SimpleNamespace(message=message)
        mock_response = types.SimpleNamespace(
            model='gpt-3.5-turbo',
            usage=usage,
            choices=[choice],
        )

        @trace
        def call_api():
            return mock_response

        # Suppress console output
        with _suppress_tracer_output(call_api):
            result = call_api()

        assert result is mock_response


class TestManualTracerAPI:
    """Task 8.3: Manual Tracer API test."""

    def test_create_trace_displays_values(self):
        """Create a Tracer with captured output, verify values appear."""
        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)
        rich_logger = RichLogger(console=console)

        tracer = Tracer(logger=rich_logger)

        tracer.create_trace(
            model='claude-3-opus',
            latency=0.85,
            input_tokens=200,
            output_tokens=400,
            cost=0.0330,
            prompt='What is Python?',
            response='Python is a programming language.',
        )

        output = string_io.getvalue()

        # Verify terminal output contains provided values
        assert 'claude-3-opus' in output
        assert '0.85' in output
        assert '200' in output
        assert '400' in output
        assert '0.0330' in output
        assert 'What is Python?' in output
        assert 'Python is a programming language.' in output


class TestTimingAccuracy:
    """Task 8.4: Timing accuracy test."""

    def test_latency_measurement(self):
        """Verify latency is measured correctly with tolerance for CI."""
        usage = types.SimpleNamespace(prompt_tokens=10, completion_tokens=20)
        message = types.SimpleNamespace(content='Response')
        choice = types.SimpleNamespace(message=message)
        mock_response = types.SimpleNamespace(
            model='gpt-4',
            usage=usage,
            choices=[choice],
        )

        @trace
        def slow_call():
            time.sleep(0.1)
            return mock_response

        # Capture the latency argument passed to capture_trace
        captured_latency = {}

        original_capture_trace = slow_call.__wrapped__  # Not used directly

        # Access the tracer instance from the closure
        tracer = _get_tracer_from_closure(slow_call)

        original_capture = tracer.capture_trace

        def mock_capture(result, latency, func_name=None):
            captured_latency['value'] = latency
            return original_capture(result=result, latency=latency, func_name=func_name)

        with mock.patch.object(tracer, 'capture_trace', side_effect=mock_capture):
            with _suppress_tracer_output_via_tracer(tracer):
                slow_call()

        # Verify latency is between 0.09 and 0.3 seconds
        assert 'value' in captured_latency, "Latency was not captured"
        assert 0.09 <= captured_latency['value'] <= 0.3, (
            f"Latency {captured_latency['value']:.4f}s is outside expected range [0.09, 0.3]"
        )


# --- Helper functions ---

class _patch_tracer_logger:
    """Context manager that patches the tracer's logger within a decorated function."""

    def __init__(self, decorated_func, new_logger):
        self.decorated_func = decorated_func
        self.new_logger = new_logger
        self.tracer = _get_tracer_from_closure(decorated_func)
        self.original_logger = self.tracer.logger if self.tracer else None

    def __enter__(self):
        if self.tracer:
            self.tracer.logger = self.new_logger
        return self

    def __exit__(self, *args):
        if self.tracer and self.original_logger is not None:
            self.tracer.logger = self.original_logger


class _suppress_tracer_output:
    """Context manager that suppresses tracer output for a decorated function."""

    def __init__(self, decorated_func):
        self.tracer = _get_tracer_from_closure(decorated_func)
        self.original_logger = self.tracer.logger if self.tracer else None

    def __enter__(self):
        if self.tracer:
            string_io = io.StringIO()
            console = Console(file=string_io, force_terminal=True, width=120)
            self.tracer.logger = RichLogger(console=console)
        return self

    def __exit__(self, *args):
        if self.tracer and self.original_logger is not None:
            self.tracer.logger = self.original_logger


class _suppress_tracer_output_via_tracer:
    """Context manager that suppresses output on a tracer instance."""

    def __init__(self, tracer):
        self.tracer = tracer
        self.original_logger = tracer.logger

    def __enter__(self):
        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)
        self.tracer.logger = RichLogger(console=console)
        return self

    def __exit__(self, *args):
        self.tracer.logger = self.original_logger


def _get_tracer_from_closure(decorated_func):
    """Extract the Tracer instance from a @trace decorated function's closure."""
    if hasattr(decorated_func, '__closure__') and decorated_func.__closure__:
        for cell in decorated_func.__closure__:
            try:
                contents = cell.cell_contents
                if isinstance(contents, Tracer):
                    return contents
            except ValueError:
                continue
    return None
