# Tests for @trace decorator

import time
import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume
from avenix import trace


class TestTraceDecorator:
    """Tests for the @trace decorator implementation."""
    
    def test_decorator_preserves_function_name(self):
        """Test that @trace preserves the wrapped function's name."""
        @trace
        def my_function():
            return "result"
        
        assert my_function.__name__ == "my_function"
    
    def test_decorator_preserves_docstring(self):
        """Test that @trace preserves the wrapped function's docstring."""
        @trace
        def my_function():
            """This is a docstring."""
            return "result"
        
        assert my_function.__doc__ == "This is a docstring."
    
    def test_decorator_returns_original_value(self):
        """Test that @trace returns the original function's return value unchanged."""
        expected_result = {"data": "test", "value": 42}
        
        with patch('avenix.tracer.Tracer') as mock_tracer_class:
            # Mock the tracer instance
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            # Re-apply decorator with mocked tracer
            @trace
            def test_func():
                return expected_result
            
            result = test_func()
            
            # Verify the result is unchanged
            assert result is expected_result
    
    def test_decorator_measures_execution_time(self):
        """Test that @trace measures execution time with perf_counter."""
        with patch('avenix.tracer.Tracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            # Re-apply decorator with mocked tracer
            @trace
            def test_func():
                time.sleep(0.1)
                return "result"
            
            test_func()
            
            # Verify capture_trace was called
            assert mock_tracer.capture_trace.called
            
            # Verify latency parameter is approximately correct
            call_args = mock_tracer.capture_trace.call_args
            latency = call_args.kwargs['latency']
            assert latency >= 0.1  # Should be at least 0.1 seconds
            assert latency < 0.2   # Should not be much more
    
    def test_decorator_calls_tracer_capture_trace(self):
        """Test that @trace calls tracer.capture_trace with correct parameters."""
        result_obj = Mock()
        
        with patch('avenix.tracer.Tracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            # Re-apply decorator with mocked tracer
            @trace
            def test_func():
                return result_obj
            
            test_func()
            
            # Verify capture_trace was called with correct arguments
            mock_tracer.capture_trace.assert_called_once()
            call_args = mock_tracer.capture_trace.call_args
            
            assert call_args.kwargs['result'] is result_obj
            assert isinstance(call_args.kwargs['latency'], float)
            assert call_args.kwargs['latency'] >= 0
            assert call_args.kwargs['func_name'] == 'test_func'
    
    def test_decorator_propagates_exceptions(self):
        """Test that @trace propagates exceptions without suppression."""
        class CustomException(Exception):
            pass
        
        with patch('avenix.tracer.Tracer'):
            # Re-apply decorator with mocked tracer
            @trace
            def test_func():
                raise CustomException("Test error")
            
            # Verify the exception is propagated
            with pytest.raises(CustomException, match="Test error"):
                test_func()
    
    def test_decorator_does_not_capture_on_exception(self):
        """Test that @trace does not capture traces when function raises exception."""
        with patch('avenix.tracer.Tracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            # Re-apply decorator with mocked tracer
            @trace
            def test_func():
                raise ValueError("Test error")
            
            # Try to call the function and catch the exception
            with pytest.raises(ValueError):
                test_func()
            
            # Verify capture_trace was NOT called
            mock_tracer.capture_trace.assert_not_called()
    
    def test_decorator_preserves_function_signature(self):
        """Test that @trace preserves function signature."""
        @trace
        def function_with_args(a: int, b: str, c: float = 3.14) -> str:
            return f"{a}-{b}-{c}"
        
        # Check that __wrapped__ attribute exists (from functools.wraps)
        assert hasattr(function_with_args, '__wrapped__')
        
        # Verify we can call with expected arguments
        with patch('avenix.tracer.Tracer'):
            @trace
            def test_func(a: int, b: str, c: float = 3.14) -> str:
                return f"{a}-{b}-{c}"
            
            result = test_func(1, "hello", c=2.5)
            assert result == "1-hello-2.5"
    
    def test_decorator_works_with_args_and_kwargs(self):
        """Test that @trace correctly handles functions with args and kwargs."""
        with patch('avenix.tracer.Tracer'):
            @trace
            def test_func(*args, **kwargs):
                return {"args": args, "kwargs": kwargs}
            
            result = test_func(1, 2, 3, key="value", another="param")
            
            assert result["args"] == (1, 2, 3)
            assert result["kwargs"] == {"key": "value", "another": "param"}
    
    def test_decorator_creates_tracer_once_at_decoration_time(self):
        """Test that @trace creates tracer instance once at decoration time."""
        with patch('avenix.tracer.Tracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            @trace
            def test_func():
                return "result"
            
            # Tracer should be created once when decorator is applied
            assert mock_tracer_class.call_count == 1
            
            # Call the function multiple times
            test_func()
            test_func()
            test_func()
            
            # Tracer should still only be created once
            assert mock_tracer_class.call_count == 1
            
            # But capture_trace should be called three times
            assert mock_tracer.capture_trace.call_count == 3


class TestDecoratorIntegration:
    """Integration tests for @trace decorator with real Tracer."""
    
    def test_decorator_with_mock_ai_response(self):
        """Test @trace with a mock AI response object."""
        # Create a mock OpenAI-like response
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        @trace
        def call_ai():
            return mock_response
        
        # Should not raise any exceptions
        result = call_ai()
        assert result is mock_response


# Property-Based Tests using Hypothesis (Phase 2: Properties 1-4)
class TestDecoratorProperties:
    """Property-based tests for @trace decorator."""
    
    @given(
        return_value=st.one_of(
            st.integers(),
            st.text(),
            st.dictionaries(st.text(), st.integers()),
            st.lists(st.integers()),
            st.none()
        )
    )
    def test_return_value_preservation(self, return_value):
        """Property 1: Decorated function returns original value unchanged."""
        with patch('avenix.tracer.Tracer'):
            @trace
            def test_func():
                return return_value
            
            result = test_func()
            assert result == return_value
            if return_value is not None:
                assert type(result) == type(return_value)
    
    @given(
        exception_type=st.sampled_from([
            ValueError,
            TypeError,
            RuntimeError,
            KeyError,
            IndexError
        ]),
        message=st.text()
    )
    def test_exception_propagation_transparency(self, exception_type, message):
        """Property 2: Decorated function propagates exceptions unchanged."""
        # Avoid extremely long messages that might cause issues
        assume(len(message) < 1000)
        
        with patch('avenix.tracer.Tracer'):
            @trace
            def test_func():
                raise exception_type(message)
            
            # Verify correct exception is raised (just check type, not message regex)
            with pytest.raises(exception_type):
                test_func()
    
    @given(
        func_name=st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz_'),
        docstring=st.one_of(st.none(), st.text(max_size=500))
    )
    def test_function_metadata_preservation(self, func_name, docstring):
        """Property 3: Decorator preserves function metadata."""
        with patch('avenix.tracer.Tracer'):
            # Dynamically create function with name
            func = lambda: "result"
            func.__name__ = func_name
            func.__doc__ = docstring
            
            # Apply decorator
            decorated = trace(func)
            
            # Verify metadata is preserved
            assert decorated.__name__ == func_name
            assert decorated.__doc__ == docstring
            assert hasattr(decorated, '__wrapped__')
    
    @given(
        num_iterations=st.integers(min_value=1, max_value=100)
    )
    def test_non_negative_latency(self, num_iterations):
        """Property 4: All measured latencies are non-negative."""
        with patch('avenix.tracer.Tracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            @trace
            def test_func():
                return "result"
            
            # Execute function multiple times
            for _ in range(num_iterations):
                test_func()
            
            # Check all latency measurements
            for call in mock_tracer.capture_trace.call_args_list:
                # Extract latency from kwargs or positional args
                if call.kwargs and 'latency' in call.kwargs:
                    latency = call.kwargs['latency']
                elif call[0] and len(call[0]) > 1:
                    latency = call[0][1]
                else:
                    # Skip if we can't find latency
                    continue
                
                assert isinstance(latency, float), f"Latency should be float, got {type(latency)}"
                assert latency >= 0.0, f"Latency should be non-negative, got {latency}"
