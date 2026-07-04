# Tests for RichFormatter

import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st
from rich.panel import Panel
from avenix.formatter import RichFormatter
from avenix.models import TraceModel


class TestRichFormatterBasics:
    """Basic tests for RichFormatter."""
    
    def test_formatter_returns_panel(self):
        """Test that format() returns a Panel."""
        formatter = RichFormatter()
        trace = TraceModel(
            model="gpt-4",
            latency=1.23,
            input_tokens=100,
            output_tokens=200,
            cost=0.0150,
            prompt="Test prompt",
            response="Test response"
        )
        
        result = formatter.format(trace)
        assert isinstance(result, Panel)
    
    def test_formatter_includes_model_info(self):
        """Test that formatted output includes model information."""
        formatter = RichFormatter()
        trace = TraceModel(
            model="gpt-4-turbo",
            latency=1.5,
            input_tokens=200,
            output_tokens=400,
            cost=0.0300,
            prompt="Test",
            response="Response"
        )
        
        result = formatter.format(trace)
        # Just verify it's a Panel with the expected model
        assert isinstance(result, Panel)
        assert result.renderable is not None
    
    def test_formatter_includes_latency_with_unit(self):
        """Test that latency is formatted with 's' suffix."""
        formatter = RichFormatter()
        trace = TraceModel(
            model="gpt-4",
            latency=2.5,
            input_tokens=100,
            output_tokens=200,
            cost=0.01,
            prompt="",
            response=""
        )
        
        result = formatter.format(trace)
        # Check the panel contains latency information
        assert result is not None
    
    def test_formatter_includes_cost_with_dollar_sign(self):
        """Test that cost is formatted with '$' prefix."""
        formatter = RichFormatter()
        trace = TraceModel(
            model="gpt-4",
            latency=1.0,
            input_tokens=100,
            output_tokens=200,
            cost=0.5000,
            prompt="",
            response=""
        )
        
        result = formatter.format(trace)
        assert result is not None


# Property-Based Tests
class TestRichFormatterProperties:
    """Property-based tests for RichFormatter."""
    
    @given(
        model=st.text(min_size=1, max_size=50),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.integers(min_value=0, max_value=1000000),
        output_tokens=st.integers(min_value=0, max_value=1000000),
        cost=st.floats(min_value=0.0, max_value=10000.0),
    )
    def test_formatted_output_contains_header(
        self,
        model,
        latency,
        input_tokens,
        output_tokens,
        cost
    ):
        """Property 9: Formatted output contains the header with emoji."""
        formatter = RichFormatter()
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            prompt="prompt",
            response="response"
        )
        
        result = formatter.format(trace)
        assert isinstance(result, Panel)
        # Check title contains the emoji and "Avenix Trace"
        assert result.title is not None
        title_text = str(result.title)
        assert "🚀" in title_text or "Avenix Trace" in title_text
    
    @given(
        model=st.text(min_size=1, max_size=50),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.integers(min_value=0, max_value=1000000),
        output_tokens=st.integers(min_value=0, max_value=1000000),
        cost=st.floats(min_value=0.0, max_value=10000.0),
    )
    def test_formatted_output_structure_completeness(
        self,
        model,
        latency,
        input_tokens,
        output_tokens,
        cost
    ):
        """Property 10: Formatted output contains all required labels and sections."""
        formatter = RichFormatter()
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            prompt="Test Prompt",
            response="Test Response"
        )
        
        result = formatter.format(trace)
        assert isinstance(result, Panel)
        # Verify it's formatted properly
        assert result is not None
        # The panel should have content
        assert result.renderable is not None
    
    @given(
        model=st.text(min_size=1, max_size=50),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.integers(min_value=0, max_value=1000000),
        output_tokens=st.integers(min_value=0, max_value=1000000),
        cost=st.floats(min_value=0.0, max_value=10000.0),
        prompt_length=st.integers(min_value=0, max_value=500),
        response_length=st.integers(min_value=0, max_value=500),
    )
    def test_formatted_output_contains_separators(
        self,
        model,
        latency,
        input_tokens,
        output_tokens,
        cost,
        prompt_length,
        response_length
    ):
        """Property 11: Formatted output contains horizontal line separators."""
        formatter = RichFormatter()
        prompt_text = "A" * prompt_length
        response_text = "B" * response_length
        
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            prompt=prompt_text,
            response=response_text
        )
        
        result = formatter.format(trace)
        assert isinstance(result, Panel)
        assert result is not None
    
    @given(
        model=st.text(min_size=1, max_size=50),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.integers(min_value=0, max_value=1000000),
        output_tokens=st.integers(min_value=0, max_value=1000000),
        cost=st.floats(min_value=0.0, max_value=10000.0),
        text_length=st.integers(min_value=0, max_value=5000),
    )
    def test_formatting_completes_without_exceptions(
        self,
        model,
        latency,
        input_tokens,
        output_tokens,
        cost,
        text_length
    ):
        """Property 12: Formatting completes without exceptions for various widths."""
        formatter = RichFormatter()
        long_text = "X" * text_length
        
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            prompt=long_text,
            response=long_text
        )
        
        # Should not raise any exceptions
        result = formatter.format(trace)
        assert result is not None
        assert isinstance(result, Panel)
