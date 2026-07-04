# Pytest fixtures and configuration

import types
import pytest

@pytest.fixture
def sample_trace_data():
    """Returns a dict with valid trace data for testing."""
    return {
        'model': 'gpt-4',
        'latency': 1.23,
        'input_tokens': 150,
        'output_tokens': 300,
        'cost': 0.0450,
        'prompt': 'Hello, how are you?',
        'response': 'I am fine, thank you!',
    }


@pytest.fixture
def mock_openai_response():
    """Returns a Mock object simulating an OpenAI ChatCompletion response."""
    usage = types.SimpleNamespace(
        prompt_tokens=150,
        completion_tokens=300,
    )
    message = types.SimpleNamespace(
        content='Hello! How can I help you today?',
    )
    choice = types.SimpleNamespace(
        message=message,
    )
    response = types.SimpleNamespace(
        model='gpt-4',
        usage=usage,
        choices=[choice],
    )
    return response


@pytest.fixture
def mock_anthropic_response():
    """Returns a Mock object simulating an Anthropic Message response."""
    usage = types.SimpleNamespace(
        input_tokens=100,
        output_tokens=200,
    )
    content_block = types.SimpleNamespace(
        text='Hello from Claude!',
    )
    response = types.SimpleNamespace(
        model='claude-3-opus',
        usage=usage,
        content=[content_block],
        role='assistant',
    )
    return response
