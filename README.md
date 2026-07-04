# Avenix v0.1

A Python tracing library for AI/LLM requests with beautiful terminal output.

Avenix provides a decorator-based API for tracing AI model requests, automatically capturing execution metrics like timing, token usage, and costs, then displaying them in richly formatted terminal output.

## Overview

Avenix simplifies monitoring AI/LLM requests by:
- **Automatic Capture**: Uses a simple `@trace` decorator to automatically capture request metrics
- **Beautiful Display**: Renders trace information in a formatted terminal panel with colors and separators
- **Multi-Provider Support**: Works with OpenAI and Anthropic model responses out of the box
- **Cost Tracking**: Automatically calculates request costs based on model pricing
- **Extensible**: Easy to add custom extractors for new AI providers

## Installation

```bash
pip install avenix
```

## Requirements

- Python 3.11+
- pydantic ^2.0
- rich ^13.0

## Quick Start

### Using the @trace Decorator

The simplest way to use Avenix is with the `@trace` decorator:

```python
from avenix import trace
from openai import OpenAI

client = OpenAI()

@trace
def get_gpt_response(prompt: str):
    """Call GPT-4 with the given prompt."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response

# When you call the function, Avenix will automatically:
# 1. Measure execution time
# 2. Extract model, tokens, and response from the result
# 3. Calculate cost based on token usage
# 4. Display formatted trace output to terminal
result = get_gpt_response("What is machine learning?")
```

### Manual Trace Creation

For more control, you can manually create traces using the `Tracer` API:

```python
from avenix import Tracer

tracer = Tracer()

# Later, manually create a trace with explicit values
tracer.create_trace(
    model="gpt-4",
    latency=2.5,
    input_tokens=150,
    output_tokens=300,
    cost=0.045,
    prompt="What is AI?",
    response="AI is artificial intelligence..."
)
```

## Supported Models

Avenix includes built-in support for:

### OpenAI
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

### Anthropic
- claude-3-opus
- claude-3-sonnet
- claude-3-haiku

## Features in v0.1

✅ Decorator-based tracing API
✅ Automatic timing measurement with perf_counter
✅ OpenAI and Anthropic response extraction
✅ Model pricing table and cost calculation
✅ Beautiful terminal output with rich formatting
✅ Error handling and graceful fallbacks
✅ Property-based test suite for correctness verification

## Out of Scope for v0.1

The following features are planned for future releases:

- Custom formatter plugins
- Database/file persistence of traces
- Trace filtering and search
- Performance statistics aggregation
- Integration with external logging services
- Support for additional AI providers
- Rate limiting and quota management
- Async/await support

## Documentation

### API Reference

#### @trace Decorator

```python
@trace
def your_function():
    # ... your code that calls an AI model
    return response
```

The `@trace` decorator:
- Measures execution time with `time.perf_counter()`
- Captures the function result
- Calls the global `Tracer` instance to extract data and display trace
- Propagates exceptions without suppression
- Preserves the original function's return value and metadata

#### Tracer Class

```python
from avenix import Tracer

tracer = Tracer(logger=None, formatter=None)
```

Methods:
- `capture_trace(result, latency, func_name=None)`: Capture and display a trace from function execution
- `create_trace(model, latency, input_tokens, output_tokens, cost, prompt, response)`: Manually create and display a trace

### TraceModel

The `TraceModel` class represents a single trace with validation:

Fields:
- `model` (str): Name of the AI model
- `latency` (float): Execution time in seconds (rounded to 2 decimals)
- `input_tokens` (int): Number of input tokens (must be non-negative)
- `output_tokens` (int): Number of output tokens (must be non-negative)
- `cost` (float): Request cost in dollars (rounded to 4 decimals, must be non-negative)
- `prompt` (str): Input prompt text (defaults to empty string)
- `response` (str): Model response text (defaults to empty string)

## Examples

See the `examples/` directory for complete working examples:

- `openai_example.py`: Using @trace with OpenAI API
- `anthropic_example.py`: Using @trace with Anthropic API
- `manual_trace.py`: Creating traces manually with Tracer API

## Testing

Avenix includes a comprehensive test suite with property-based tests:

```bash
pytest tests/ -v                    # Run all tests
pytest tests/ --cov                 # Run with coverage report
pytest tests/test_models.py -v      # Run specific test file
```

Test coverage targets:
- Core modules (decorator, tracer, models, formatter, extractors): >90%
- Property-based tests for 16 correctness properties
- Unit tests for all feature components

## Architecture

Avenix follows a layered architecture:

1. **Models Layer** (`models.py`): Defines `TraceModel` with Pydantic validation
2. **Decorator Layer** (`decorator.py`): Provides `@trace` decorator for wrapping functions
3. **Tracer Layer** (`tracer.py`): Core orchestration with optional custom logger/formatter
4. **Extraction Layer** (`extractors.py`): Provider-specific response extractors
5. **Formatting Layer** (`formatter.py`): Beautiful terminal output with rich library
6. **Logging Layer** (`logger.py`): Terminal display with fallback handling

## Error Handling

Avenix is designed to be resilient to errors:

- **Extraction Failures**: If response format doesn't match known providers, uses sensible defaults
- **Validation Failures**: If TraceModel validation fails, falls back to defaults
- **Rendering Failures**: If rich formatting fails, falls back to basic print output
- **Exception Propagation**: Errors in traced functions propagate normally without suppression

## Contributing

This is a v0.1 release. Feedback and contributions are welcome!

## API Reference

For detailed API documentation, see [API.md](API.md).

## License

MIT License - See LICENSE file for details

## Changelog

See CHANGELOG.md for version history and release notes
