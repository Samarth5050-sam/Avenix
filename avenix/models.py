# Data models for AgentForge tracing

from pydantic import BaseModel, Field, field_validator


class TraceModel(BaseModel):
    """
    Data model for a single AI request trace.
    
    All fields are validated by Pydantic for type safety.
    """
    
    model: str = Field(
        description="Name of the AI model used (e.g., 'gpt-4', 'claude-3')"
    )
    
    latency: float = Field(
        ge=0.0,
        description="Request latency in seconds"
    )
    
    input_tokens: int = Field(
        ge=0,
        description="Number of tokens in the input/prompt"
    )
    
    output_tokens: int = Field(
        ge=0,
        description="Number of tokens in the output/response"
    )
    
    cost: float = Field(
        ge=0.0,
        description="Request cost in USD"
    )
    
    prompt: str = Field(
        default="",
        description="Input prompt text"
    )
    
    response: str = Field(
        default="",
        description="Output response text"
    )
    
    @field_validator('latency')
    @classmethod
    def round_latency(cls, v: float) -> float:
        """Round latency to 2 decimal places."""
        return round(v, 2)
    
    @field_validator('cost')
    @classmethod
    def round_cost(cls, v: float) -> float:
        """Round cost to 4 decimal places."""
        return round(v, 4)


# Model pricing table (prices per 1K tokens in USD)
MODEL_PRICING = {
    # OpenAI models
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    
    # Anthropic models
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost in USD based on model and token counts.
    
    Args:
        model: Name of the AI model (e.g., 'gpt-4', 'claude-3-opus')
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/response tokens
    
    Returns:
        Cost in USD, rounded to 4 decimal places
        Returns 0.0 for unknown models
    
    Formula:
        (input_tokens / 1000) * input_price + (output_tokens / 1000) * output_price
    """
    if model not in MODEL_PRICING:
        return 0.0
    
    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    
    return round(input_cost + output_cost, 4)
