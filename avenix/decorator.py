# Trace decorator implementation

import functools
import time
from typing import Callable, Any


def trace(func: Callable) -> Callable:
    """
    Decorator that traces AI request function execution.
    
    Captures timing, model info, tokens, cost, prompt, and response.
    Displays formatted trace to terminal after execution.
    
    Args:
        func: The function to trace (should return AI response object)
    
    Returns:
        Wrapped function with identical signature and return type
        
    Example:
        @trace
        def call_openai(prompt: str):
            return client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
    """
    from .tracer import Tracer
    
    # Create tracer instance once at decoration time
    tracer = Tracer()
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Record start time with high precision
        start_time = time.perf_counter()
        
        try:
            # Execute the wrapped function
            result = func(*args, **kwargs)
            
            # Calculate latency
            end_time = time.perf_counter()
            latency = end_time - start_time
            
            # Capture and display trace
            tracer.capture_trace(
                result=result,
                latency=latency,
                func_name=func.__name__
            )
            
            # Return original result unchanged
            return result
            
        except Exception:
            # Propagate exceptions without suppression
            # No trace is captured on failure
            raise
    
    return wrapper
