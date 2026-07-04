# Implementation Plan: AgentForge v0.1 Tracing Library

## Overview

This implementation plan breaks down the AgentForge v0.1 tracing library into discrete, actionable tasks following the six implementation phases from the design document. Each task is focused on implementing specific components with clear acceptance criteria tied to requirements and correctness properties.

The library provides a decorator-based API for tracing AI requests, automatically capturing timing, token usage, costs, prompts, and responses, then displaying them in beautifully formatted terminal output.

## Tasks

### Phase 1: Core Data Model

- [x] 1. Set up project structure and core data model
  - [x] 1.1 Create Python package directory structure
    - Create `agentforge/` directory with `__init__.py`
    - Create empty module files: `models.py`, `decorator.py`, `tracer.py`, `extractors.py`, `formatter.py`, `logger.py`
    - Set up `tests/` directory with `__init__.py` and test module files
    - Create `examples/` directory
    - _Requirements: 7.1_

  - [x] 1.2 Create `pyproject.toml` with package metadata and dependencies
    - Define package metadata (name, version 0.1.0, description)
    - Specify Python 3.11+ requirement
    - Add dependencies: pydantic ^2.0, rich ^13.0
    - Add dev dependencies: pytest ^8.0, hypothesis ^6.0, pytest-cov ^4.0, pytest-mock ^3.0
    - _Requirements: 7.2, 7.3_

  - [x] 1.3 Implement TraceModel with Pydantic validation in `models.py`
    - Create TraceModel class with fields: model, latency, input_tokens, output_tokens, cost, prompt, response
    - Add field validators for latency (round to 2 decimals, non-negative)
    - Add field validators for cost (round to 4 decimals, non-negative)
    - Add field validators for token counts (non-negative integers)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [x]* 1.4 Write property test for TraceModel field validation
    - **Property 6: TraceModel Field Validation**
    - **Validates: Requirements 3.1-3.8**
    - Generate valid/invalid data with hypothesis
    - Verify acceptance of valid data and rejection/coercion of invalid data
    - Test all field types and constraints

  - [x]* 1.5 Write property test for latency precision
    - **Property 5: Latency Precision**
    - **Validates: Requirements 2.4**
    - Generate random float latency values
    - Verify values are rounded to exactly 2 decimal places in TraceModel

  - [x] 1.6 Implement model pricing table and cost calculation function in `models.py`
    - Create MODEL_PRICING dictionary with OpenAI and Anthropic pricing
    - Implement calculate_cost(model, input_tokens, output_tokens) function
    - Formula: (input_tokens / 1000) * input_price + (output_tokens / 1000) * output_price
    - Round result to 4 decimal places
    - Return 0.0 for unknown models
    - _Requirements: 11.3_

  - [x]* 1.7 Write property test for cost calculation accuracy
    - **Property 7: Cost Calculation Accuracy**
    - **Validates: Requirements 11.3**
    - Generate random token counts and use known model pricing
    - Verify calculated cost matches expected formula
    - Test edge cases (zero tokens, large token counts)

  - [x]* 1.8 Write property test for cost precision
    - **Property 8: Cost Precision**
    - **Validates: Requirements 4.6**
    - Generate random float cost values
    - Verify costs are rounded to exactly 4 decimal places in TraceModel

### Phase 2: Decorator and Tracer Core

- [x] 2. Implement trace decorator and tracer orchestration
  - [x] 2.1 Implement @trace decorator in `decorator.py`
    - Use functools.wraps to preserve function metadata
    - Measure execution time with time.perf_counter()
    - Capture function result and latency
    - Call tracer.capture_trace() with result and timing
    - Propagate exceptions without suppression
    - Return original function result unchanged
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3_

  - [x]* 2.2 Write property test for return value preservation
    - **Property 1: Return Value Preservation**
    - **Validates: Requirements 1.3**
    - Generate functions returning various types (int, str, dict, list, None)
    - Decorate with @trace and verify return values match undecorated versions
    - Use hypothesis strategies for diverse inputs

  - [x]* 2.3 Write property test for exception propagation
    - **Property 2: Exception Propagation Transparency**
    - **Validates: Requirements 1.4, 10.3**
    - Generate functions that raise various exception types
    - Decorate with @trace and verify exceptions propagate unchanged
    - Ensure no trace is displayed on exception

  - [x]* 2.4 Write property test for function metadata preservation
    - **Property 3: Function Metadata Preservation**
    - **Validates: Requirements 1.5**
    - Generate functions with various __name__, __doc__, __module__ values
    - Decorate with @trace and verify all metadata attributes preserved

  - [x]* 2.5 Write property test for non-negative latency
    - **Property 4: Non-Negative Latency**
    - **Validates: Requirements 2.3**
    - Execute decorated functions multiple times
    - Verify all measured latencies are >= 0.0

  - [x] 2.6 Implement Tracer class core structure in `tracer.py`
    - Create Tracer class with __init__(logger, formatter)
    - Initialize with default RichLogger and RichFormatter if not provided
    - Store logger and formatter as instance attributes
    - _Requirements: 6.1_

  - [x] 2.7 Implement capture_trace() method in Tracer
    - Accept result, latency, func_name parameters
    - Call _extract_trace_data(result) to get extracted data
    - Calculate cost using calculate_cost() from models
    - Create TraceModel with extracted data and latency
    - Handle ValidationError with fallback to default TraceModel
    - Call _display_trace() to format and log
    - _Requirements: 6.2, 6.3, 10.1, 10.4_

  - [x] 2.8 Implement create_trace() method in Tracer
    - Accept model, latency, input_tokens, output_tokens, cost, prompt, response parameters
    - Create TraceModel from provided parameters
    - Call _display_trace() to format and log
    - _Requirements: 6.2, 6.3, 6.4_

  - [-] 2.9 Implement _display_trace() helper method in Tracer
    - Accept TraceModel parameter
    - Call formatter.format(trace) to get renderable
    - Call logger.log(renderable) to display
    - Wrap in try-except to handle formatting/logging errors gracefully
    - _Requirements: 5.1, 5.3, 10.2_

- [x] 3. Checkpoint - Verify decorator and tracer integration
  - Ensure all tests pass, ask the user if questions arise.

### Phase 3: Extraction Logic

- [x] 4. Implement provider-specific extraction logic
  - [-] 4.1 Create extractor base class and OpenAI extractor in `extractors.py`
    - Create ResponseExtractor abstract base class with can_extract() and extract() methods
    - Implement OpenAIExtractor class
    - Implement can_extract() to check for model, usage, and choices attributes
    - Implement extract() to extract model, tokens, and response from OpenAI format
    - Handle AttributeError and IndexError with logging and empty dict return
    - _Requirements: 11.5_

  - [ ] 4.2 Implement Anthropic extractor in `extractors.py`
    - Implement AnthropicExtractor class extending ResponseExtractor
    - Implement can_extract() to check for model, usage, and content attributes
    - Implement extract() to extract model, tokens, and response from Anthropic format
    - Handle AttributeError and IndexError with logging and empty dict return
    - _Requirements: 11.5_

  - [x] 4.3 Implement extraction chain in Tracer
    - Add extractors list to Tracer.__init__() with OpenAI and Anthropic extractors
    - Implement _extract_trace_data(result) method
    - Iterate through extractors, call can_extract() and extract()
    - Return extracted dict on first successful extraction
    - Log warning and return fallback dict if no extractor matches
    - Fallback: model='unknown', input_tokens=0, output_tokens=0, prompt='', response=str(result)[:500]
    - _Requirements: 11.1, 11.2, 11.4_

  - [x]* 4.4 Write property test for extraction failure resilience
    - **Property 13: Extraction Failure Resilience**
    - **Validates: Requirements 10.1, 11.4**
    - Generate objects that don't match known provider formats
    - Verify Tracer.capture_trace() completes without exceptions
    - Verify default values used (model='unknown', tokens=0, cost=0.0)

  - [x]* 4.5 Write property test for token extraction completeness
    - **Property 16: Token Extraction Completeness**
    - **Validates: Requirements 11.1, 11.2**
    - Create mock OpenAI and Anthropic responses with various token counts
    - Verify both input_tokens and output_tokens extracted correctly
    - Test with hypothesis-generated token values

  - [x]* 4.6 Write unit tests for provider-specific formats
    - Test OpenAI response format with complete valid data
    - Test Anthropic response format with complete valid data
    - Test extraction with missing fields (partial data)
    - Test extraction with invalid attributes

### Phase 4: Formatting and Display

- [x] 5. Implement terminal formatting and display
  - [x] 5.1 Implement RichFormatter class in `formatter.py`
    - Create RichFormatter class with format(trace) method
    - Build metadata section with Model, Latency, Input, Output, Cost labels
    - Format latency with 2 decimals and 's' suffix
    - Format cost with 4 decimals and '$' prefix
    - Build Prompt section with separator lines
    - Build Response section with separator lines
    - Use rich.text.Text for styled composition
    - Wrap in rich.panel.Panel with title "🚀 AgentForge Trace"
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

  - [x]* 5.2 Write property test for formatted output header
    - **Property 9: Formatted Output Contains Header**
    - **Validates: Requirements 4.1**
    - Generate random TraceModel instances
    - Format and verify output contains "🚀 AgentForge Trace"

  - [x]* 5.3 Write property test for formatted output structure completeness
    - **Property 10: Formatted Output Structure Completeness**
    - **Validates: Requirements 4.2-4.8**
    - Generate random TraceModel instances with hypothesis
    - Format and verify all required labels present: Model:, Latency:, Input:, Output:, Cost:, Prompt, Response
    - Verify latency has 2 decimals and 's', cost has 4 decimals and '$'

  - [x]* 5.4 Write property test for formatted output separators
    - **Property 11: Formatted Output Contains Separators**
    - **Validates: Requirements 4.9**
    - Generate random TraceModel instances
    - Format and verify horizontal line characters (━) present in output

  - [x]* 5.5 Write property test for terminal width robustness
    - **Property 12: Terminal Width Robustness**
    - **Validates: Requirements 5.4**
    - Generate TraceModel instances with various text lengths
    - Mock different terminal widths
    - Verify formatting completes without exceptions for all widths

  - [x] 5.6 Implement RichLogger class in `logger.py`
    - Create RichLogger class with __init__(console) method
    - Initialize with default rich.console.Console() if not provided
    - Implement log(renderable) method
    - Use console.print(renderable) to display
    - Wrap in try-except to catch rendering errors
    - Fallback to basic print() with error message on failure
    - _Requirements: 5.1, 5.2, 5.3, 10.2_

  - [x]* 5.7 Write property test for rendering failure resilience
    - **Property 14: Rendering Failure Resilience**
    - **Validates: Requirements 10.2**
    - Mock rich library rendering failures
    - Verify Logger.log() does not raise exceptions
    - Verify fallback mechanism triggers

  - [x]* 5.8 Write property test for validation failure fallback
    - **Property 15: Validation Failure Fallback**
    - **Validates: Requirements 10.4, 10.5**
    - Generate invalid TraceModel data (negative values, wrong types)
    - Verify system creates TraceModel with defaults or coercion
    - Verify no application crashes

- [x] 6. Checkpoint - Verify formatting and display integration
  - Ensure all tests pass, ask the user if questions arise.

### Phase 5: Package Structure and Distribution

- [x] 7. Wire components and finalize package structure
  - [x] 7.1 Implement public API exports in `agentforge/__init__.py`
    - Import trace from decorator
    - Import Tracer from tracer
    - Define __all__ = ["trace", "Tracer"]
    - Define __version__ = "0.1.0"
    - _Requirements: 1.1, 6.1, 7.7_

  - [x]* 7.2 Write unit tests for package imports
    - Test `from agentforge import trace` succeeds
    - Test `from agentforge import Tracer` succeeds
    - Verify __version__ attribute accessible
    - Verify no internal modules exposed

  - [x] 7.3 Create README.md with documentation
    - Write introduction and overview
    - Add installation instructions (pip install)
    - Add quick start example with @trace decorator
    - Add manual Tracer API example
    - Document what's in scope and out of scope for v0.1
    - Add requirements and dependencies section
    - _Requirements: 7.4, 12.1, 12.3, 12.5_

  - [x] 7.4 Create LICENSE file
    - Add MIT License text
    - _Requirements: 7.5_

  - [x] 7.5 Create CHANGELOG.md
    - Add v0.1.0 section with initial release features
    - _Requirements: 7.6_

  - [x] 7.6 Create .gitignore file
    - Add Python standard ignores: __pycache__, *.pyc, .pytest_cache, .coverage
    - Add build artifacts: dist/, build/, *.egg-info
    - Add IDE files: .vscode/, .idea/

  - [x] 7.7 Create OpenAI example script in `examples/openai_example.py`
    - Write example using @trace with mock OpenAI client
    - Add inline comments explaining the code
    - _Requirements: 9.5, 12.2_

  - [x] 7.8 Create Anthropic example script in `examples/anthropic_example.py`
    - Write example using @trace with mock Anthropic client
    - Add inline comments explaining the code
    - _Requirements: 9.5, 12.2_

  - [x] 7.9 Create manual trace example script in `examples/manual_trace.py`
    - Write example using Tracer.create_trace() API
    - Demonstrate manual trace creation with explicit values
    - Add inline comments explaining the code
    - _Requirements: 9.5, 12.2_

### Phase 6: Testing and Documentation

- [x] 8. Complete test suite and documentation
  - [x] 8.1 Create pytest configuration in `tests/conftest.py`
    - Define sample_trace_data fixture with valid trace data
    - Define mock_openai_response fixture
    - Define mock_anthropic_response fixture
    - _Requirements: 9.4_

  - [x]* 8.2 Write integration test for end-to-end decorator usage
    - Test @trace decorator with mock OpenAI response
    - Capture terminal output
    - Verify trace displayed correctly
    - Verify function returns correct value
    - _Requirements: 9.1_

  - [x]* 8.3 Write integration test for manual Tracer API
    - Test Tracer.create_trace() with explicit values
    - Capture terminal output
    - Verify trace displayed with provided values
    - _Requirements: 9.1_

  - [x]* 8.4 Write integration test for timing accuracy
    - Decorate function with known sleep duration
    - Verify latency measurement is accurate within tolerance
    - _Requirements: 2.3_

  - [x] 8.5 Add inline documentation to all public methods
    - Add docstrings to @trace decorator
    - Add docstrings to Tracer.__init__, capture_trace, create_trace
    - Add docstrings to TraceModel class and fields
    - Follow Google docstring format
    - _Requirements: 12.4_

  - [x]* 8.6 Run test coverage report
    - Execute pytest with coverage
    - Verify >90% line coverage for core modules (decorator, tracer, models, formatter, extractors)
    - _Requirements: 9.1, 9.2, 9.3_

  - [x] 8.7 Write API reference documentation
    - Document @trace decorator signature and behavior
    - Document Tracer class with all public methods
    - Document TraceModel fields and validation rules
    - Add to README or separate API.md file
    - _Requirements: 12.3_

- [x] 9. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.
  - Verify all 16 correctness properties have passing tests
  - Verify package installs successfully
  - Run all example scripts to confirm they work
  - Review documentation for completeness

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- All property-based tests should use hypothesis with minimum 100 iterations
- Each test task references specific correctness properties from the design document
- Test tasks are distributed across implementation phases to catch errors early
- Mock objects should be used for AI provider responses to avoid external dependencies
- Terminal output capture in tests can use `io.StringIO` or `pytest capsys` fixture
- The implementation follows a bottom-up approach: data model → core logic → UI → integration
- Checkpoint tasks ensure incremental validation and provide opportunities for user feedback

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "1.6"] },
    { "id": 2, "tasks": ["1.4", "1.5", "1.7", "1.8"] },
    { "id": 3, "tasks": ["2.1", "2.6"] },
    { "id": 4, "tasks": ["2.2", "2.3", "2.4", "2.5", "2.7", "2.8"] },
    { "id": 5, "tasks": ["2.9", "4.1", "4.2"] },
    { "id": 6, "tasks": ["4.3"] },
    { "id": 7, "tasks": ["4.4", "4.5", "4.6"] },
    { "id": 8, "tasks": ["5.1"] },
    { "id": 9, "tasks": ["5.2", "5.3", "5.4", "5.5", "5.6"] },
    { "id": 10, "tasks": ["5.7", "5.8"] },
    { "id": 11, "tasks": ["7.1"] },
    { "id": 12, "tasks": ["7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9", "8.1"] },
    { "id": 13, "tasks": ["8.2", "8.3", "8.4", "8.5"] },
    { "id": 14, "tasks": ["8.6", "8.7"] }
  ]
}
```
