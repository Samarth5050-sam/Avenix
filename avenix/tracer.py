# Core tracer implementation

import logging
from types import SimpleNamespace
from typing import Any, Optional

from pydantic import ValidationError

from .models import TraceModel, calculate_cost

logger = logging.getLogger(__name__)
_TRACE_MODEL_CLASS = TraceModel


def _build_fallback_trace(
    model: str = 'unknown',
    latency: float = 0.0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost: float = 0.0,
    prompt: str = '',
    response: str = '',
):
    """Return a sanitized trace model, falling back to a simple object if needed."""
    sanitized = {
        'model': model or 'unknown',
        'latency': max(0.0, latency or 0.0),
        'input_tokens': max(0, input_tokens or 0),
        'output_tokens': max(0, output_tokens or 0),
        'cost': max(0.0, cost or 0.0),
        'prompt': prompt or '',
        'response': response or '',
    }

    try:
        return _TRACE_MODEL_CLASS(**sanitized)
    except Exception:
        return SimpleNamespace(**sanitized)


class Tracer:
    """Core tracing engine for Avenix."""
    
    def __init__(self, logger=None, formatter=None):
        """
        Initialize tracer with optional custom logger and formatter.
        
        Args:
            logger: Custom logger instance (defaults to RichLogger)
            formatter: Custom formatter instance (defaults to RichFormatter)
        """
        # Lazy import to avoid circular dependencies
        if logger is None:
            from .logger import RichLogger
            self.logger = RichLogger()
        else:
            self.logger = logger
            
        if formatter is None:
            from .formatter import RichFormatter
            self.formatter = RichFormatter()
        else:
            self.formatter = formatter
    
    def capture_trace(
        self,
        result: Any,
        latency: float,
        func_name: Optional[str] = None
    ) -> None:
        """
        Capture and display a trace from function execution result.
        
        Args:
            result: Return value from traced function
            latency: Execution time in seconds
            func_name: Optional name of traced function
        """
        # Extract trace data from result
        extracted = self._extract_trace_data(result)
        
        # Calculate cost
        cost = calculate_cost(
            extracted.get('model', 'unknown'),
            extracted.get('input_tokens', 0),
            extracted.get('output_tokens', 0)
        )
        
        try:
            # Create validated trace model
            trace = TraceModel(
                model=extracted.get('model', 'unknown'),
                latency=latency,
                input_tokens=extracted.get('input_tokens', 0),
                output_tokens=extracted.get('output_tokens', 0),
                cost=cost,
                prompt=extracted.get('prompt', ''),
                response=extracted.get('response', '')
            )
        except ValidationError as e:
            logger.error(f"Trace validation failed: {e}")
            trace = _build_fallback_trace(
                model='unknown',
                latency=latency,
                response='[Validation failed]',
            )
        except Exception as e:
            logger.error(f"Unexpected error creating trace: {e}")
            trace = _build_fallback_trace(
                model='unknown',
                latency=latency,
                response='[Validation failed]',
            )
        
        # Display the trace
        self._display_trace(trace)
    
    def create_trace(
        self,
        model: str,
        latency: float,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        prompt: str,
        response: str
    ) -> None:
        """
        Manually create and display a trace with explicit values.
        
        Args:
            model: Name of the AI model used
            latency: Request latency in seconds
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Request cost in dollars
            prompt: Input prompt text
            response: Response text from AI
        """
        try:
            trace = TraceModel(
                model=model,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                prompt=prompt,
                response=response
            )
        except Exception as e:
            logger.error(f"Trace creation failed: {e}")
            trace = _build_fallback_trace(
                model=model,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                prompt=prompt,
                response=response,
            )
        
        self._display_trace(trace)
    
    def _extract_trace_data(self, result: Any) -> dict:
        """
        Extract trace data using chain of extractors.
        
        Returns dict with partial or complete trace data.
        Missing fields will use default values.
        """
        # Lazy import extractors
        from .extractors import OpenAIExtractor, AnthropicExtractor
        
        extractors = [
            OpenAIExtractor(),
            AnthropicExtractor(),
        ]
        
        try:
            for extractor in extractors:
                if extractor.can_extract(result):
                    data = extractor.extract(result)
                    if data:  # Extractor returned something
                        return data
        except Exception as e:
            logger.warning(f"Extraction failed: {e}", exc_info=True)
        
        # Fallback to minimal data if no extractor matched
        logger.warning(
            f"No extractor found for result type: {type(result).__name__}"
        )
        return {
            'model': 'unknown',
            'input_tokens': 0,
            'output_tokens': 0,
            'prompt': '',
            'response': str(result)[:500]  # Fallback to string repr
        }
    
    def _display_trace(self, trace: TraceModel) -> None:
        """
        Display a trace to the terminal.
        
        Args:
            trace: The trace model to display
        """
        try:
            formatted = self.formatter.format(trace)
            self.logger.log(formatted)
        except Exception as e:
            logger.error(f"Failed to display trace: {e}", exc_info=True)
            # Fallback to basic output
            print(f"[Avenix] Model: {trace.model}, "
                  f"Latency: {trace.latency:.2f}s, "
                  f"Cost: ${trace.cost:.4f}")
