# Tests for RichLogger

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st
from rich.console import Console
from rich.panel import Panel
from avenix.logger import RichLogger
from avenix.formatter import RichFormatter
from avenix.models import TraceModel


class TestRichLoggerBasics:
    """Basic tests for RichLogger."""
    
    def test_logger_initializes_with_default_console(self):
        """Test that RichLogger initializes with default console."""
        logger = RichLogger()
        assert logger.console is not None
        assert isinstance(logger.console, Console)
    
    def test_logger_initializes_with_custom_console(self):
        """Test that RichLogger accepts custom console."""
        custom_console = Console()
        logger = RichLogger(console=custom_console)
        assert logger.console is custom_console
    
    def test_logger_log_calls_console_print(self):
        """Test that log() calls console.print()."""
        mock_console = Mock()
        logger = RichLogger(console=mock_console)
        
        renderable = Mock()
        logger.log(renderable)
        
        mock_console.print.assert_called_once_with(renderable)
    
    def test_logger_log_handles_exceptions(self):
        """Test that log() handles exceptions gracefully."""
        mock_console = Mock()
        mock_console.print.side_effect = Exception("Console error")
        logger = RichLogger(console=mock_console)
        
        renderable = Mock()
        # Should not raise exception
        with patch('builtins.print'):
            logger.log(renderable)
    
    def test_logger_log_with_real_panel(self):
        """Test logger with real Panel object."""
        logger = RichLogger()
        
        panel = Panel("Test content", title="Test Title")
        # Should not raise any exceptions
        logger.log(panel)


class TestRichLoggerIntegration:
    """Integration tests for RichLogger with formatter."""
    
    def test_logger_with_formatted_trace(self):
        """Test logger displays formatted trace correctly."""
        logger = RichLogger()
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
        
        formatted = formatter.format(trace)
        # Should not raise any exceptions
        logger.log(formatted)


# Property-Based Tests
class TestRichLoggerProperties:
    """Property-based tests for RichLogger."""
    
    @given(
        content=st.text(max_size=5000),
    )
    def test_rendering_failure_resilience(self, content):
        """Property 14: Logger handles rendering failures gracefully."""
        # Mock a console that fails
        mock_console = Mock()
        mock_console.print.side_effect = Exception("Rendering failed")
        
        logger = RichLogger(console=mock_console)
        
        # Create a renderable
        renderable = Mock()
        
        # Should not raise exception
        with patch('builtins.print'):  # Mock print to avoid actual output
            logger.log(renderable)
        
        # Console.print should have been called
        mock_console.print.assert_called_once_with(renderable)
    
    @given(
        model=st.text(min_size=1, max_size=50),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.integers(min_value=0, max_value=1000000),
        output_tokens=st.integers(min_value=0, max_value=1000000),
        cost=st.floats(min_value=0.0, max_value=10000.0),
    )
    def test_validation_failure_fallback(
        self,
        model,
        latency,
        input_tokens,
        output_tokens,
        cost
    ):
        """Property 15: System creates valid TraceModel with defaults or coercion."""
        logger = RichLogger()
        formatter = RichFormatter()
        
        # Create trace with potentially problematic values
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            prompt="Valid prompt",
            response="Valid response"
        )
        
        # Should format successfully
        formatted = formatter.format(trace)
        assert formatted is not None
        
        # Should log successfully without raising exceptions
        logger.log(formatted)
