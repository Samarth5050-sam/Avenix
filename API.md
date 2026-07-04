# Avenix v0.1 — API Reference

Complete API documentation for the Avenix tracing library.

---

## Table of Contents

- [@trace Decorator](#trace-decorator)
- [Tracer Class](#tracer-class)
- [TraceModel](#tracemodel)
- [Cost Calculation](#cost-calculation)
- [Supported Providers](#supported-providers)

---

## @trace Decorator

The `@trace` decorator is the primary entry point for automatic tracing of AI/LLM function calls.

### Import

```python
from avenix import trace
```

### Signature

```python
def trace(func: Callable) -> Callable
```

| Parameter | Type       | Description                                           |
|-----------|------------|-------------------------------------------------------|
| `func`    | `Callable` | The function to trace. Should return an AI response object. |

**Returns:** A wrapped function with an identical signature and return type (via `functools.wraps`).

### Behavior

When a function decorated with `@trace` is called:

1. **Timing** — Records the start time using `time.perf_counter()` for high-precision measurement.
2. **Execution** — Executes the original function with all positional and keyword arguments.
3. **Latency calculation** — Computes `latency = end_time - start_time` in seconds.
4. **Trace capture** — Calls `Tracer.capture_trace(result, latency, func_name)` on an internal `Tracer` instance that is created once at decoration time.
5. **Return** — Returns the original function's result unchanged.

### Exception Handling

- If the wrapped function raises an exception, it is **re-raised immediately** without suppression.
- **No trace is captured** when an exception occurs.
- The decorator does not introduce any additional exception types.

### Example: OpenAI

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

# Automatically traces timing, tokens, cost, and displays formatted output
result = get_gpt_response("Explain quantum computing in one paragraph.")
```

### Example: Anthropic

```python
from avenix import trace
import anthropic

client = anthropic.Anthropic()

@trace
def get_claude_response(prompt: str):
    """Call Claude 3 Sonnet with the given prompt."""
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response

result = get_claude_response("What is deep learning?")
```

---

## Tracer Class

The `Tracer` class is the core tracing engine. It orchestrates data extraction, cost calculation, validation, formatting, and display.

### Import

```python
from avenix import Tracer
```

### Constructor

```python
Tracer(logger=None, formatter=None)
```

| Parameter   | Type              | Default          | Description                                                                 |
|-------------|-------------------|------------------|-----------------------------------------------------------------------------|
| `logger`    | `object \| None`  | `RichLogger()`   | Custom logger instance. Must expose a `.log(formatted_str)` method. Defaults to the built-in `RichLogger` for terminal output. |
| `formatter` | `object \| None`  | `RichFormatter()`| Custom formatter instance. Must expose a `.format(trace) -> str` method. Defaults to the built-in `RichFormatter` for rich panel output. |

### Methods

#### `capture_trace(result, latency, func_name=None)`

Captures and displays a trace by automatically extracting data from an AI provider response object.

```python
tracer.capture_trace(result, latency, func_name=None)
```

| Parameter   | Type             | Default | Description                                                    |
|-------------|------------------|---------|----------------------------------------------------------------|
| `result`    | `Any`            | —       | The return value from a traced function (e.g., an OpenAI or Anthropic response object). |
| `latency`   | `float`          | —       | Execution time in seconds.                                     |
| `func_name` | `str \| None`    | `None`  | Optional name of the traced function (used for logging context). |

**Returns:** `None`

**Behavior:**

1. Runs the result through the extractor chain (`OpenAIExtractor` → `AnthropicExtractor`). The first extractor that recognizes the response format extracts model name, token counts, and response text.
2. Calculates cost via `calculate_cost(model, input_tokens, output_tokens)`.
3. Creates a validated `TraceModel` instance. On validation failure, falls back to a sanitized `SimpleNamespace` with safe defaults.
4. Formats and displays the trace via the configured formatter and logger.

---

#### `create_trace(model, latency, input_tokens, output_tokens, cost, prompt, response)`

Manually creates and displays a trace with explicit values. Useful when you want full control over trace data or are not using a supported provider.

```python
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

| Parameter       | Type   | Description                          |
|-----------------|--------|--------------------------------------|
| `model`         | `str`  | Name of the AI model used.           |
| `latency`       | `float`| Request latency in seconds.          |
| `input_tokens`  | `int`  | Number of input/prompt tokens.       |
| `output_tokens` | `int`  | Number of output/response tokens.    |
| `cost`          | `float`| Request cost in USD.                 |
| `prompt`        | `str`  | Input prompt text.                   |
| `response`      | `str`  | Response text from the AI model.     |

**Returns:** `None`

**Behavior:**

1. Attempts to create a validated `TraceModel` instance from the provided values.
2. On validation failure, falls back to a sanitized fallback trace with clamped non-negative values.
3. Formats and displays the trace.

---

## TraceModel

`TraceModel` is a [Pydantic `BaseModel`](https://docs.pydantic.dev/) that represents a single AI request trace with built-in validation.

### Import

```python
from avenix.models import TraceModel
```

### Fields

| Field           | Type    | Default | Constraints                                      | Description                                    |
|-----------------|---------|---------|--------------------------------------------------|------------------------------------------------|
| `model`         | `str`   | —       | Required                                         | Name of the AI model (e.g., `"gpt-4"`, `"claude-3-opus"`). |
| `latency`       | `float` | —       | `>= 0.0`, rounded to **2 decimal places**       | Request latency in seconds.                    |
| `input_tokens`  | `int`   | —       | `>= 0`                                           | Number of tokens in the input/prompt.          |
| `output_tokens` | `int`   | —       | `>= 0`                                           | Number of tokens in the output/response.       |
| `cost`          | `float` | —       | `>= 0.0`, rounded to **4 decimal places**       | Request cost in USD.                           |
| `prompt`        | `str`   | `""`    | —                                                | Input prompt text.                             |
| `response`      | `str`   | `""`    | —                                                | Output response text.                          |

### Validation Rules

- **`latency`** — Must be non-negative (`>= 0.0`). Automatically rounded to 2 decimal places via `@field_validator`.
- **`cost`** — Must be non-negative (`>= 0.0`). Automatically rounded to 4 decimal places via `@field_validator`.
- **`input_tokens`** — Must be a non-negative integer (`>= 0`).
- **`output_tokens`** — Must be a non-negative integer (`>= 0`).
- **`model`** — Required string (no default); must be provided.
- **`prompt`** and **`response`** — Default to empty strings if not provided.

### Example

```python
from avenix.models import TraceModel

trace = TraceModel(
    model="gpt-4",
    latency=1.2345,       # → stored as 1.23
    input_tokens=100,
    output_tokens=250,
    cost=0.01895123,       # → stored as 0.019
    prompt="Hello, world!",
    response="Hi there!"
)

print(trace.latency)   # 1.23
print(trace.cost)      # 0.019
```

---

## Cost Calculation

The `calculate_cost` function computes the USD cost of an AI request based on the model and token usage.

### Import

```python
from avenix.models import calculate_cost
```

### Signature

```python
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float
```

| Parameter       | Type   | Description                                          |
|-----------------|--------|------------------------------------------------------|
| `model`         | `str`  | Name of the AI model (must match a key in the pricing table). |
| `input_tokens`  | `int`  | Number of input/prompt tokens.                       |
| `output_tokens` | `int`  | Number of output/response tokens.                    |

**Returns:** Cost in USD, rounded to 4 decimal places. Returns `0.0` for unknown models.

### Formula

```
cost = (input_tokens / 1000) × input_price + (output_tokens / 1000) × output_price
```

### Supported Models & Pricing

Prices are **per 1,000 tokens** in USD.

| Model              | Input Price  | Output Price |
|--------------------|-------------|--------------|
| `gpt-4`            | $0.03       | $0.06        |
| `gpt-4-turbo`      | $0.01       | $0.03        |
| `gpt-3.5-turbo`    | $0.0005     | $0.0015      |
| `claude-3-opus`    | $0.015      | $0.075       |
| `claude-3-sonnet`  | $0.003      | $0.015       |
| `claude-3-haiku`   | $0.00025    | $0.00125     |

### Example

```python
from avenix.models import calculate_cost

# GPT-4: 500 input tokens, 200 output tokens
cost = calculate_cost("gpt-4", input_tokens=500, output_tokens=200)
# cost = (500/1000)*0.03 + (200/1000)*0.06 = 0.015 + 0.012 = 0.027
print(cost)  # 0.027

# Unknown model returns 0.0
cost = calculate_cost("unknown-model", 100, 100)
print(cost)  # 0.0
```

---

## Supported Providers

Avenix ships with built-in extractors for OpenAI and Anthropic response formats. The extractors are tried in order; the first one that matches handles the response.

### OpenAI Response Format

The `OpenAIExtractor` detects responses that have:

| Attribute                          | Description                          |
|------------------------------------|--------------------------------------|
| `result.model`                     | Model name string (e.g., `"gpt-4"`) |
| `result.usage.prompt_tokens`       | Number of input tokens               |
| `result.usage.completion_tokens`   | Number of output/completion tokens   |
| `result.choices[0].message.content`| Response text from the model         |

**Detection logic:** The result must have a `model` attribute, a `usage` object with `prompt_tokens` and `completion_tokens`, and a `choices` attribute that is a list or tuple.

### Anthropic Response Format

The `AnthropicExtractor` detects responses that have:

| Attribute                      | Description                              |
|--------------------------------|------------------------------------------|
| `result.model`                 | Model name string (e.g., `"claude-3-sonnet-20240229"`) |
| `result.usage.input_tokens`    | Number of input tokens                   |
| `result.usage.output_tokens`   | Number of output tokens                  |
| `result.content[0].text`       | Response text from the model             |

**Detection logic:** The result must have a `model` attribute, a `usage` object with `input_tokens` and `output_tokens`, and a `content` attribute that is a list or tuple.

### Extraction Fallback

If no extractor matches the response format:

- `model` defaults to `"unknown"`
- `input_tokens` and `output_tokens` default to `0`
- `prompt` defaults to `""`
- `response` defaults to `str(result)[:500]` (truncated string representation)

---

## Error Handling Summary

Avenix is designed to be resilient at every layer:

| Layer                | Failure Behavior                                                                 |
|----------------------|----------------------------------------------------------------------------------|
| **Extraction**       | Falls back to defaults (`model="unknown"`, tokens=`0`, response=`str(result)[:500]`) |
| **TraceModel validation** | Falls back to a sanitized `SimpleNamespace` with clamped non-negative values  |
| **Formatting/Display** | Falls back to a basic `print()` with model, latency, and cost                 |
| **Traced function exception** | Exception propagates unchanged; no trace is captured                    |
