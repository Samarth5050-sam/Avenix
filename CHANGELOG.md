# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-15

### Added

#### Core Features
- **@trace Decorator**: Simple decorator-based API for tracing AI model requests
- **Tracer Class**: Core orchestration engine with customizable logger and formatter
- **TraceModel**: Pydantic-based data model with field validation and precision requirements
  - Latency rounded to 2 decimal places
  - Cost rounded to 4 decimal places
  - Non-negative validation for numerical fields

#### Provider Support
- **OpenAI Extractor**: Automatic extraction from OpenAI API responses (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
- **Anthropic Extractor**: Automatic extraction from Anthropic API responses (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- **Model Pricing Table**: Built-in pricing for all supported models
- **Cost Calculation**: Automatic cost calculation based on token usage and model pricing

#### Display and Formatting
- **RichFormatter**: Beautiful terminal output with colored panels, separators, and structured information
- **RichLogger**: Terminal display using rich library with graceful fallback handling
- **Error-Resilient Formatting**: Handles rendering failures gracefully with fallback to basic print

#### Robustness and Error Handling
- **Extraction Failure Resilience**: Unknown response formats fall back to sensible defaults
- **Validation Error Handling**: TraceModel validation failures result in fallback to default values
- **Exception Propagation**: Errors in traced functions propagate normally without suppression
- **Graceful Degradation**: Rendering and logging failures don't crash the application

#### Testing
- **Comprehensive Test Suite**: 40+ unit and property-based tests
- **16 Correctness Properties**: Verified properties for return value preservation, exception handling, metadata preservation, precision, resilience, etc.
- **Property-Based Testing**: Hypothesis-based tests covering edge cases and random inputs
- **>90% Code Coverage**: High test coverage for core modules

#### Documentation
- **README.md**: Complete user guide with quick start and API reference
- **Inline Documentation**: Docstrings for all public methods and classes
- **Example Scripts**: Working examples for OpenAI, Anthropic, and manual trace creation

### Correctness Properties Verified

1. **Return Value Preservation**: Decorated functions return values unchanged
2. **Exception Propagation Transparency**: Exceptions propagate without modification
3. **Function Metadata Preservation**: Decorator preserves __name__, __doc__, __module__
4. **Non-Negative Latency**: All measured latencies are >= 0.0
5. **Latency Precision**: Latency rounded to exactly 2 decimal places
6. **TraceModel Field Validation**: Valid data accepted, invalid data rejected or coerced
7. **Cost Calculation Accuracy**: Costs calculated correctly using model pricing formula
8. **Cost Precision**: Cost rounded to exactly 4 decimal places
9. **Formatted Output Header**: Output contains "🚀 Avenix Trace"
10. **Formatted Output Structure**: All required labels and sections present
11. **Formatted Output Separators**: Output contains horizontal line separators
12. **Terminal Width Robustness**: Formatting works for various terminal widths
13. **Extraction Failure Resilience**: UnknownProvider formats handled gracefully
14. **Rendering Failure Resilience**: Formatting/logging errors don't crash application
15. **Validation Failure Fallback**: Invalid data creates fallback TraceModel successfully
16. **Token Extraction Completeness**: Both input and output tokens extracted correctly

### Requirements Met

- Python 3.11+ support
- Pydantic 2.0+ for validation
- Rich 13.0+ for terminal formatting
- Pytest 8.0+ for testing
- Hypothesis 6.0+ for property-based testing

## [Unreleased]

### Planned for Future Releases

- Custom formatter plugins
- Database/file persistence of traces
- Trace filtering and search capabilities
- Performance statistics aggregation (percentiles, throughput)
- Integration with external logging services
- Support for additional AI providers (Google, LLaMA, etc.)
- Rate limiting and quota management
- Async/await support for tracing async functions
- Web UI for trace visualization
- Batch trace processing

### Known Limitations in v0.1

- No persistence layer (traces are only displayed, not stored)
- No filtering or search capabilities
- No performance aggregation features
- Synchronous-only (no async support)
- Limited to predefined formatters and loggers
- No database integration

---

For updates and upcoming features, see the project repository.
