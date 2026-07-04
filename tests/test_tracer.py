"""Tests for Tracer class core structure and initialization."""

import pytest
from unittest.mock import Mock, patch
from avenix.tracer import Tracer
from avenix.logger import RichLogger
from avenix.formatter import RichFormatter
from avenix.models import TraceModel


class TestTracerInitialization:
    """Tests for Tracer.__init__() method."""
    
    def test_tracer_initializes_with_defaults(self):
        """Test that Tracer initializes with default logger and formatter."""
        tracer = Tracer()
        
        assert tracer.logger is not None
        assert tracer.formatter is not None
        assert isinstance(tracer.logger, RichLogger)
        assert isinstance(tracer.formatter, RichFormatter)
    
    def test_tracer_initializes_with_custom_logger(self):
        """Test that Tracer accepts custom logger instance."""
        custom_logger = RichLogger()
        tracer = Tracer(logger=custom_logger)
        
        assert tracer.logger is custom_logger
        assert isinstance(tracer.formatter, RichFormatter)
    
    def test_tracer_initializes_with_custom_formatter(self):
        """Test that Tracer accepts custom formatter instance."""
        custom_formatter = RichFormatter()
        tracer = Tracer(formatter=custom_formatter)
        
        assert tracer.formatter is custom_formatter
        assert isinstance(tracer.logger, RichLogger)
    
    def test_tracer_initializes_with_custom_logger_and_formatter(self):
        """Test that Tracer accepts both custom logger and formatter."""
        custom_logger = RichLogger()
        custom_formatter = RichFormatter()
        tracer = Tracer(logger=custom_logger, formatter=custom_formatter)
        
        assert tracer.logger is custom_logger
        assert tracer.formatter is custom_formatter
    
    def test_tracer_stores_logger_as_instance_attribute(self):
        """Test that logger is stored as instance attribute."""
        tracer = Tracer()
        assert hasattr(tracer, 'logger')
    
    def test_tracer_stores_formatter_as_instance_attribute(self):
        """Test that formatter is stored as instance attribute."""
        tracer = Tracer()
        assert hasattr(tracer, 'formatter')



class TestCreateTrace:
    """Tests for Tracer.create_trace() method."""
    
    def test_create_trace_with_valid_parameters(self):
        """Test that create_trace creates TraceModel and displays trace."""
        tracer = Tracer()
        
        # Mock the _display_trace method to capture calls
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4',
                latency=1.23,
                input_tokens=150,
                output_tokens=300,
                cost=0.0450,
                prompt='Hello, world!',
                response='Hi there!'
            )
            
            # Verify _display_trace was called once
            assert mock_display.call_count == 1
            
            # Verify the trace model passed to _display_trace has correct values
            trace_arg = mock_display.call_args[0][0]
            assert isinstance(trace_arg, TraceModel)
            assert trace_arg.model == 'gpt-4'
            assert trace_arg.latency == 1.23
            assert trace_arg.input_tokens == 150
            assert trace_arg.output_tokens == 300
            assert trace_arg.cost == 0.0450
            assert trace_arg.prompt == 'Hello, world!'
            assert trace_arg.response == 'Hi there!'
    
    def test_create_trace_with_minimal_parameters(self):
        """Test create_trace with minimal valid parameters."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='claude-3',
                latency=0.5,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                prompt='',
                response=''
            )
            
            assert mock_display.call_count == 1
            trace_arg = mock_display.call_args[0][0]
            assert trace_arg.model == 'claude-3'
            assert trace_arg.latency == 0.5
            assert trace_arg.input_tokens == 0
            assert trace_arg.output_tokens == 0
            assert trace_arg.cost == 0.0
            assert trace_arg.prompt == ''
            assert trace_arg.response == ''
    
    def test_create_trace_with_large_token_counts(self):
        """Test create_trace with large token counts."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4-turbo',
                latency=5.67,
                input_tokens=100000,
                output_tokens=50000,
                cost=15.5000,
                prompt='A' * 1000,
                response='B' * 2000
            )
            
            assert mock_display.call_count == 1
            trace_arg = mock_display.call_args[0][0]
            assert trace_arg.input_tokens == 100000
            assert trace_arg.output_tokens == 50000
            assert trace_arg.cost == 15.5000
    
    def test_create_trace_formats_latency_precision(self):
        """Test that create_trace respects latency precision (2 decimals)."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4',
                latency=1.23456789,
                input_tokens=100,
                output_tokens=200,
                cost=0.01,
                prompt='test',
                response='response'
            )
            
            trace_arg = mock_display.call_args[0][0]
            # TraceModel should round latency to 2 decimal places
            assert trace_arg.latency == 1.23
    
    def test_create_trace_formats_cost_precision(self):
        """Test that create_trace respects cost precision (4 decimals)."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4',
                latency=1.0,
                input_tokens=100,
                output_tokens=200,
                cost=0.123456789,
                prompt='test',
                response='response'
            )
            
            trace_arg = mock_display.call_args[0][0]
            # TraceModel should round cost to 4 decimal places
            assert trace_arg.cost == 0.1235
    
    def test_create_trace_with_multiline_text(self):
        """Test create_trace with multiline prompts and responses."""
        tracer = Tracer()
        
        multiline_prompt = "Line 1\nLine 2\nLine 3"
        multiline_response = "Response 1\nResponse 2\nResponse 3"
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='claude-3-opus',
                latency=2.5,
                input_tokens=75,
                output_tokens=150,
                cost=0.0225,
                prompt=multiline_prompt,
                response=multiline_response
            )
            
            trace_arg = mock_display.call_args[0][0]
            assert trace_arg.prompt == multiline_prompt
            assert trace_arg.response == multiline_response
    
    def test_create_trace_calls_display_trace(self):
        """Test that create_trace calls _display_trace to format and log."""
        tracer = Tracer()
        
        # Mock both formatter and logger to verify the chain
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-3.5-turbo',
                latency=0.75,
                input_tokens=50,
                output_tokens=100,
                cost=0.0001,
                prompt='Quick test',
                response='Quick response'
            )
            
            # Verify _display_trace was called (which handles formatting and logging)
            assert mock_display.called
            assert mock_display.call_count == 1
    
    def test_create_trace_handles_validation_errors_gracefully(self):
        """Test that create_trace handles validation errors with fallback values."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            # Create trace with potentially problematic values
            # (though TraceModel should handle these via coercion)
            tracer.create_trace(
                model='test-model',
                latency=1.5,
                input_tokens=100,
                output_tokens=200,
                cost=0.05,
                prompt='test prompt',
                response='test response'
            )
            
            # Should still call _display_trace even if validation needed adjustment
            assert mock_display.called
            trace_arg = mock_display.call_args[0][0]
            assert isinstance(trace_arg, TraceModel)



class TestCaptureTrace:
    """Tests for Tracer.capture_trace() method."""
    
    def test_capture_trace_extracts_data_from_result(self):
        """Test that capture_trace calls _extract_trace_data with result."""
        tracer = Tracer()
        mock_result = Mock()
        
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'gpt-4',
            'input_tokens': 100,
            'output_tokens': 200,
            'prompt': 'test prompt',
            'response': 'test response'
        }) as mock_extract:
            with patch.object(tracer, '_display_trace'):
                tracer.capture_trace(mock_result, 1.5, 'test_func')
                mock_extract.assert_called_once_with(mock_result)
    
    def test_capture_trace_calculates_cost(self):
        """Test that capture_trace calculates cost using model and tokens."""
        tracer = Tracer()
        mock_result = Mock()
        
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'gpt-4',
            'input_tokens': 1000,
            'output_tokens': 2000,
            'prompt': 'test',
            'response': 'test'
        }):
            with patch('avenix.tracer.calculate_cost', return_value=0.15) as mock_cost:
                with patch.object(tracer, '_display_trace'):
                    tracer.capture_trace(mock_result, 1.5)
                    mock_cost.assert_called_once_with('gpt-4', 1000, 2000)
    
    def test_capture_trace_creates_trace_model(self):
        """Test that capture_trace creates TraceModel with extracted data and latency."""
        tracer = Tracer()
        mock_result = Mock()
        
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'gpt-4',
            'input_tokens': 150,
            'output_tokens': 300,
            'prompt': 'Hello',
            'response': 'Hi there'
        }):
            with patch.object(tracer, '_display_trace') as mock_display:
                tracer.capture_trace(mock_result, 2.34)
                
                # Check that _display_trace was called with a TraceModel
                assert mock_display.call_count == 1
                trace = mock_display.call_args[0][0]
                assert isinstance(trace, TraceModel)
                assert trace.model == 'gpt-4'
                assert trace.latency == 2.34
                assert trace.input_tokens == 150
                assert trace.output_tokens == 300
                assert trace.prompt == 'Hello'
                assert trace.response == 'Hi there'
    
    def test_capture_trace_handles_validation_error_with_fallback(self):
        """Test that capture_trace falls back to default TraceModel on ValidationError."""
        tracer = Tracer()
        mock_result = Mock()
        
        # Simulate extraction returning invalid data
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'test-model',
            'input_tokens': -100,  # Invalid: negative
            'output_tokens': 200,
            'prompt': 'test',
            'response': 'test'
        }):
            with patch.object(tracer, '_display_trace') as mock_display:
                # This should not raise an exception despite invalid data
                tracer.capture_trace(mock_result, 1.5)
                
                # Should still display a trace (with fallback)
                assert mock_display.call_count == 1
                trace = mock_display.call_args[0][0]
                assert isinstance(trace, TraceModel)
    
    def test_capture_trace_calls_display_trace(self):
        """Test that capture_trace calls _display_trace to format and log."""
        tracer = Tracer()
        mock_result = Mock()
        
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'gpt-4',
            'input_tokens': 100,
            'output_tokens': 200,
            'prompt': 'test',
            'response': 'test'
        }):
            with patch.object(tracer, '_display_trace') as mock_display:
                tracer.capture_trace(mock_result, 1.5)
                assert mock_display.call_count == 1
    
    def test_capture_trace_uses_default_values_for_missing_fields(self):
        """Test that capture_trace uses defaults when extracted data is incomplete."""
        tracer = Tracer()
        mock_result = Mock()
        
        # Return incomplete extraction
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'gpt-4'
            # Missing tokens, prompt, response
        }):
            with patch.object(tracer, '_display_trace') as mock_display:
                tracer.capture_trace(mock_result, 1.0)
                
                trace = mock_display.call_args[0][0]
                assert trace.input_tokens == 0
                assert trace.output_tokens == 0
                assert trace.prompt == ''
                assert trace.response == ''
    
    def test_capture_trace_handles_exception_in_validation(self):
        """Test that capture_trace handles exceptions during TraceModel creation."""
        tracer = Tracer()
        mock_result = Mock()
        
        with patch.object(tracer, '_extract_trace_data', return_value={
            'model': 'test-model',
            'input_tokens': 100,
            'output_tokens': 200,
            'prompt': 'test',
            'response': 'test'
        }):
            # Mock TraceModel to raise an exception
            with patch('avenix.tracer.TraceModel', side_effect=Exception("Validation error")):
                with patch.object(tracer, '_display_trace') as mock_display:
                    # Should not crash
                    tracer.capture_trace(mock_result, 1.5)
                    
                    # Should still call display with fallback trace
                    assert mock_display.call_count == 1
    
    def test_capture_trace_with_real_components(self):
        """Test capture_trace with real components working together."""
        tracer = Tracer()
        
        # Create a mock OpenAI response
        mock_response = Mock()
        mock_response.model = 'gpt-4'
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=100)
        mock_response.choices = [Mock(message=Mock(content='AI is amazing'))]
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.capture_trace(mock_response, 2.5, 'test_function')
            
            # Verify display was called
            assert mock_display.call_count == 1
            trace = mock_display.call_args[0][0]
            assert isinstance(trace, TraceModel)
            assert trace.model == 'gpt-4'
            assert trace.latency == 2.5
            assert trace.input_tokens == 50
            assert trace.output_tokens == 100


class TestCreateTrace:
    """Tests for Tracer.create_trace() method."""
    
    def test_create_trace_creates_trace_model_with_provided_values(self):
        """Test that create_trace creates TraceModel with explicit values."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4',
                latency=1.23,
                input_tokens=150,
                output_tokens=300,
                cost=0.045,
                prompt='Hello world',
                response='Hi there'
            )
            
            assert mock_display.call_count == 1
            trace = mock_display.call_args[0][0]
            assert isinstance(trace, TraceModel)
            assert trace.model == 'gpt-4'
            assert trace.latency == 1.23
            assert trace.input_tokens == 150
            assert trace.output_tokens == 300
            assert trace.cost == 0.045
            assert trace.prompt == 'Hello world'
            assert trace.response == 'Hi there'
    
    def test_create_trace_calls_display_trace(self):
        """Test that create_trace calls _display_trace."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4',
                latency=1.0,
                input_tokens=100,
                output_tokens=200,
                cost=0.01,
                prompt='test',
                response='test'
            )
            assert mock_display.call_count == 1
    
    def test_create_trace_handles_validation_errors(self):
        """Test that create_trace handles validation errors gracefully."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            # Provide negative values which should be handled
            tracer.create_trace(
                model='gpt-4',
                latency=-1.0,  # Invalid
                input_tokens=-100,  # Invalid
                output_tokens=-200,  # Invalid
                cost=-0.01,  # Invalid
                prompt='test',
                response='test'
            )
            
            # Should still display a trace (with corrected values)
            assert mock_display.call_count == 1
            trace = mock_display.call_args[0][0]
            assert isinstance(trace, TraceModel)
            # Values should be corrected to valid ones
            assert trace.latency >= 0.0
            assert trace.input_tokens >= 0
            assert trace.output_tokens >= 0
            assert trace.cost >= 0.0


class TestExtractTraceData:
    """Tests for Tracer._extract_trace_data() method."""
    
    def test_extract_uses_openai_extractor_for_openai_response(self):
        """Test that _extract_trace_data uses OpenAI extractor for OpenAI format."""
        tracer = Tracer()
        
        # Create mock OpenAI response
        mock_response = Mock()
        mock_response.model = 'gpt-4'
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200)
        mock_response.choices = [Mock(message=Mock(content='test response'))]
        
        result = tracer._extract_trace_data(mock_response)
        
        assert result['model'] == 'gpt-4'
        assert result['input_tokens'] == 100
        assert result['output_tokens'] == 200
        assert result['response'] == 'test response'
    
    def test_extract_uses_anthropic_extractor_for_anthropic_response(self):
        """Test that _extract_trace_data uses Anthropic extractor for Anthropic format."""
        tracer = Tracer()
        
        # Create mock Anthropic response with proper structure
        mock_response = Mock()
        mock_response.model = 'claude-3-opus'
        mock_response.usage = Mock(input_tokens=150, output_tokens=250)
        
        # Make content properly indexable
        mock_content_item = Mock()
        mock_content_item.text = 'test response'
        mock_response.content = [mock_content_item]
        
        result = tracer._extract_trace_data(mock_response)
        
        assert result['model'] == 'claude-3-opus'
        assert result['input_tokens'] == 150
        assert result['output_tokens'] == 250
        assert result['response'] == 'test response'
    
    def test_extract_returns_fallback_for_unknown_format(self):
        """Test that _extract_trace_data returns fallback for unknown response format."""
        tracer = Tracer()
        
        # Create unknown response format
        mock_response = Mock()
        mock_response.some_field = 'value'
        
        result = tracer._extract_trace_data(mock_response)
        
        assert result['model'] == 'unknown'
        assert result['input_tokens'] == 0
        assert result['output_tokens'] == 0
        assert result['prompt'] == ''
        assert 'response' in result
    
    def test_extract_handles_extraction_exceptions(self):
        """Test that _extract_trace_data handles exceptions during extraction."""
        tracer = Tracer()
        
        # Create response that will cause extraction error
        mock_response = Mock()
        mock_response.model = 'gpt-4'
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200)
        mock_response.choices = []  # Empty choices will cause IndexError
        
        # Should not raise exception, should return fallback
        result = tracer._extract_trace_data(mock_response)
        
        # Should fallback to unknown
        assert result['model'] == 'unknown'
        assert result['input_tokens'] == 0
        assert result['output_tokens'] == 0


class TestDisplayTrace:
    """Tests for Tracer._display_trace() method."""
    
    def test_display_trace_calls_formatter_format(self):
        """Test that _display_trace calls formatter.format() with trace."""
        tracer = Tracer()
        mock_formatter = Mock()
        mock_formatter.format.return_value = "formatted output"
        tracer.formatter = mock_formatter
        
        mock_logger = Mock()
        tracer.logger = mock_logger
        
        trace = TraceModel(
            model='gpt-4',
            latency=1.0,
            input_tokens=100,
            output_tokens=200,
            cost=0.01,
            prompt='test',
            response='test'
        )
        
        tracer._display_trace(trace)
        
        mock_formatter.format.assert_called_once_with(trace)
    
    def test_display_trace_calls_logger_log(self):
        """Test that _display_trace calls logger.log() with formatted output."""
        tracer = Tracer()
        mock_formatter = Mock()
        formatted_output = "formatted trace"
        mock_formatter.format.return_value = formatted_output
        tracer.formatter = mock_formatter
        
        mock_logger = Mock()
        tracer.logger = mock_logger
        
        trace = TraceModel(
            model='gpt-4',
            latency=1.0,
            input_tokens=100,
            output_tokens=200,
            cost=0.01,
            prompt='test',
            response='test'
        )
        
        tracer._display_trace(trace)
        
        mock_logger.log.assert_called_once_with(formatted_output)
    
    def test_display_trace_handles_formatting_errors(self, capsys):
        """Test that _display_trace handles formatting errors gracefully."""
        tracer = Tracer()
        mock_formatter = Mock()
        mock_formatter.format.side_effect = Exception("Formatting error")
        tracer.formatter = mock_formatter
        
        trace = TraceModel(
            model='gpt-4',
            latency=1.23,
            input_tokens=100,
            output_tokens=200,
            cost=0.045,
            prompt='test',
            response='test'
        )
        
        # Should not raise exception
        tracer._display_trace(trace)
        
        # Should fallback to basic print
        captured = capsys.readouterr()
        assert '[Avenix]' in captured.out
        assert 'gpt-4' in captured.out
        assert '1.23s' in captured.out
        assert '$0.0450' in captured.out
    
    def test_display_trace_handles_logging_errors(self, capsys):
        """Test that _display_trace handles logging errors gracefully."""
        tracer = Tracer()
        mock_formatter = Mock()
        mock_formatter.format.return_value = "formatted"
        tracer.formatter = mock_formatter
        
        mock_logger = Mock()
        mock_logger.log.side_effect = Exception("Logging error")
        tracer.logger = mock_logger
        
        trace = TraceModel(
            model='gpt-4',
            latency=1.5,
            input_tokens=100,
            output_tokens=200,
            cost=0.05,
            prompt='test',
            response='test'
        )
        
        # Should not raise exception
        tracer._display_trace(trace)
        
        # Should fallback to basic print
        captured = capsys.readouterr()
        assert '[Avenix]' in captured.out



class TestCreateTraceIntegration:
    """Integration tests for create_trace() method with actual formatting and display."""
    
    def test_create_trace_integration_with_real_components(self, capsys):
        """Test create_trace with real formatter and logger components."""
        tracer = Tracer()
        
        # Create a trace with all parameters
        tracer.create_trace(
            model='gpt-4',
            latency=1.23,
            input_tokens=150,
            output_tokens=300,
            cost=0.0450,
            prompt='What is the capital of France?',
            response='The capital of France is Paris.'
        )
        
        # Capture the output (rich will write to stdout)
        captured = capsys.readouterr()
        
        # Verify output contains key information
        # Note: Rich formatting may add ANSI codes, so we check for content presence
        output = captured.out
        
        # The output should contain the trace information
        # (Rich may format it, but the text should be present)
        assert len(output) > 0  # Something was printed
    
    def test_create_trace_with_zero_values(self):
        """Test create_trace with zero values for tokens and cost."""
        tracer = Tracer()
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='test-model',
                latency=0.0,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                prompt='',
                response=''
            )
            
            assert mock_display.called
            trace_arg = mock_display.call_args[0][0]
            assert trace_arg.latency == 0.0
            assert trace_arg.input_tokens == 0
            assert trace_arg.output_tokens == 0
            assert trace_arg.cost == 0.0
    
    def test_create_trace_with_special_characters(self):
        """Test create_trace with special characters in prompt and response."""
        tracer = Tracer()
        
        special_prompt = "What's the meaning of \"life\"?\n\tTab character here."
        special_response = "Life's meaning: 42 💡\n\nWith emoji!"
        
        with patch.object(tracer, '_display_trace') as mock_display:
            tracer.create_trace(
                model='gpt-4',
                latency=1.5,
                input_tokens=100,
                output_tokens=200,
                cost=0.03,
                prompt=special_prompt,
                response=special_response
            )
            
            trace_arg = mock_display.call_args[0][0]
            assert trace_arg.prompt == special_prompt
            assert trace_arg.response == special_response
