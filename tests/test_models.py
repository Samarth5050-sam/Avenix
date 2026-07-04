# Tests for TraceModel validation and cost calculation

import pytest
from hypothesis import given, strategies as st
from avenix.models import TraceModel, MODEL_PRICING, calculate_cost


class TestTraceModel:
    """Test suite for TraceModel validation."""
    
    def test_valid_trace_model(self):
        """Test creating a valid TraceModel."""
        trace = TraceModel(
            model="gpt-4",
            latency=1.234,
            input_tokens=100,
            output_tokens=200,
            cost=0.0150,
            prompt="Test prompt",
            response="Test response"
        )
        
        assert trace.model == "gpt-4"
        assert trace.latency == 1.23  # Rounded to 2 decimals
        assert trace.input_tokens == 100
        assert trace.output_tokens == 200
        assert trace.cost == 0.0150  # Rounded to 4 decimals
        assert trace.prompt == "Test prompt"
        assert trace.response == "Test response"
    
    def test_latency_rounding(self):
        """Test latency is rounded to 2 decimal places."""
        trace = TraceModel(
            model="gpt-4",
            latency=1.23456789,
            input_tokens=100,
            output_tokens=200,
            cost=0.0150
        )
        assert trace.latency == 1.23
    
    def test_cost_rounding(self):
        """Test cost is rounded to 4 decimal places."""
        trace = TraceModel(
            model="gpt-4",
            latency=1.0,
            input_tokens=100,
            output_tokens=200,
            cost=0.0150123456
        )
        assert trace.cost == 0.0150
    
    def test_default_prompt_and_response(self):
        """Test prompt and response default to empty strings."""
        trace = TraceModel(
            model="gpt-4",
            latency=1.0,
            input_tokens=100,
            output_tokens=200,
            cost=0.0150
        )
        assert trace.prompt == ""
        assert trace.response == ""
    
    def test_negative_latency_rejected(self):
        """Test that negative latency is rejected."""
        with pytest.raises(ValueError):
            TraceModel(
                model="gpt-4",
                latency=-1.0,
                input_tokens=100,
                output_tokens=200,
                cost=0.0150
            )
    
    def test_negative_tokens_rejected(self):
        """Test that negative token counts are rejected."""
        with pytest.raises(ValueError):
            TraceModel(
                model="gpt-4",
                latency=1.0,
                input_tokens=-100,
                output_tokens=200,
                cost=0.0150
            )
        
        with pytest.raises(ValueError):
            TraceModel(
                model="gpt-4",
                latency=1.0,
                input_tokens=100,
                output_tokens=-200,
                cost=0.0150
            )
    
    def test_negative_cost_rejected(self):
        """Test that negative cost is rejected."""
        with pytest.raises(ValueError):
            TraceModel(
                model="gpt-4",
                latency=1.0,
                input_tokens=100,
                output_tokens=200,
                cost=-0.0150
            )


class TestModelPricing:
    """Test suite for MODEL_PRICING table."""
    
    def test_model_pricing_has_openai_models(self):
        """Test MODEL_PRICING contains OpenAI models."""
        assert "gpt-4" in MODEL_PRICING
        assert "gpt-4-turbo" in MODEL_PRICING
        assert "gpt-3.5-turbo" in MODEL_PRICING
    
    def test_model_pricing_has_anthropic_models(self):
        """Test MODEL_PRICING contains Anthropic models."""
        assert "claude-3-opus" in MODEL_PRICING
        assert "claude-3-sonnet" in MODEL_PRICING
        assert "claude-3-haiku" in MODEL_PRICING
    
    def test_model_pricing_structure(self):
        """Test each model has input and output pricing."""
        for model, pricing in MODEL_PRICING.items():
            assert "input" in pricing, f"{model} missing input price"
            assert "output" in pricing, f"{model} missing output price"
            assert isinstance(pricing["input"], (int, float)), f"{model} input price not numeric"
            assert isinstance(pricing["output"], (int, float)), f"{model} output price not numeric"
            assert pricing["input"] >= 0, f"{model} input price is negative"
            assert pricing["output"] >= 0, f"{model} output price is negative"


class TestCalculateCost:
    """Test suite for calculate_cost function."""
    
    def test_gpt4_cost_calculation(self):
        """Test cost calculation for GPT-4."""
        # GPT-4: input=$0.03/1K, output=$0.06/1K
        # 1000 input tokens = $0.03
        # 2000 output tokens = $0.12
        # Total = $0.15
        cost = calculate_cost("gpt-4", 1000, 2000)
        assert cost == 0.1500
    
    def test_gpt35_turbo_cost_calculation(self):
        """Test cost calculation for GPT-3.5-turbo."""
        # GPT-3.5-turbo: input=$0.0005/1K, output=$0.0015/1K
        # 1000 input tokens = $0.0005
        # 1000 output tokens = $0.0015
        # Total = $0.0020
        cost = calculate_cost("gpt-3.5-turbo", 1000, 1000)
        assert cost == 0.0020
    
    def test_claude_opus_cost_calculation(self):
        """Test cost calculation for Claude 3 Opus."""
        # Claude-3-opus: input=$0.015/1K, output=$0.075/1K
        # 2000 input tokens = $0.03
        # 1000 output tokens = $0.075
        # Total = $0.105
        cost = calculate_cost("claude-3-opus", 2000, 1000)
        assert cost == 0.1050
    
    def test_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        cost = calculate_cost("gpt-4", 0, 0)
        assert cost == 0.0
    
    def test_small_token_counts(self):
        """Test cost calculation with small token counts."""
        # GPT-4: 10 input, 20 output
        # Cost = (10/1000)*0.03 + (20/1000)*0.06 = 0.0003 + 0.0012 = 0.0015
        cost = calculate_cost("gpt-4", 10, 20)
        assert cost == 0.0015
    
    def test_unknown_model_returns_zero(self):
        """Test that unknown models return 0.0 cost."""
        cost = calculate_cost("unknown-model", 1000, 1000)
        assert cost == 0.0
    
    def test_cost_rounding_to_four_decimals(self):
        """Test that cost is rounded to 4 decimal places."""
        # GPT-4: 1 input, 1 output
        # Cost = (1/1000)*0.03 + (1/1000)*0.06 = 0.00003 + 0.00006 = 0.00009
        # Rounded to 4 decimals = 0.0001
        cost = calculate_cost("gpt-4", 1, 1)
        assert cost == 0.0001
    
    def test_all_models_in_pricing_table(self):
        """Test cost calculation works for all models in pricing table."""
        for model in MODEL_PRICING:
            cost = calculate_cost(model, 1000, 1000)
            assert cost >= 0.0, f"Cost for {model} should be non-negative"
            assert isinstance(cost, float), f"Cost for {model} should be float"


# Property-Based Tests using Hypothesis
class TestTraceModelProperties:
    """Property-based tests for TraceModel (Properties 5-8)."""
    
    @given(
        model=st.text(min_size=1),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.integers(min_value=0, max_value=1000000),
        output_tokens=st.integers(min_value=0, max_value=1000000),
        cost=st.floats(min_value=0.0, max_value=10000.0),
        prompt=st.text(),
        response=st.text()
    )
    def test_valid_data_accepted(self, model, latency, input_tokens, output_tokens, cost, prompt, response):
        """Property 6: TraceModel accepts valid data."""
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            prompt=prompt,
            response=response
        )
        assert trace.model == model
        assert trace.input_tokens == input_tokens
        assert trace.output_tokens == output_tokens
    
    @given(
        model=st.just("gpt-4"),
        latency=st.floats(min_value=0.0, max_value=1000.0),
        input_tokens=st.just(100),
        output_tokens=st.just(200),
        cost=st.just(0.1)
    )
    def test_latency_precision_exactly_two_decimals(self, model, latency, input_tokens, output_tokens, cost):
        """Property 5: Latency is precisely rounded to 2 decimal places."""
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost
        )
        # Verify latency has exactly 2 decimal places (or fewer if trailing zeros)
        # Round to 2 decimals to check precision
        rounded_latency = round(latency, 2)
        assert trace.latency == rounded_latency
        # Verify by converting to string and checking decimal places
        latency_str = f"{trace.latency:.2f}"
        decimal_part = latency_str.split(".")[1]
        assert len(decimal_part) <= 2
    
    @given(
        model=st.sampled_from(list(MODEL_PRICING.keys())),
        input_tokens=st.integers(min_value=0, max_value=10000),
        output_tokens=st.integers(min_value=0, max_value=10000)
    )
    def test_cost_calculation_accuracy(self, model, input_tokens, output_tokens):
        """Property 7: Cost calculation matches formula exactly."""
        cost = calculate_cost(model, input_tokens, output_tokens)
        
        # Manually calculate expected cost
        pricing = MODEL_PRICING[model]
        input_price = pricing["input"]
        output_price = pricing["output"]
        expected_cost = (input_tokens / 1000) * input_price + (output_tokens / 1000) * output_price
        expected_cost = round(expected_cost, 4)
        
        assert cost == expected_cost, f"Calculated {cost} but expected {expected_cost} for model {model}"
    
    @given(
        model=st.just("gpt-4"),
        latency=st.just(1.0),
        input_tokens=st.just(100),
        output_tokens=st.just(200),
        cost=st.floats(min_value=0.0, max_value=10000.0)
    )
    def test_cost_precision_exactly_four_decimals(self, model, latency, input_tokens, output_tokens, cost):
        """Property 8: Cost is precisely rounded to 4 decimal places."""
        trace = TraceModel(
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost
        )
        # Verify cost has exactly 4 decimal places (or fewer if trailing zeros)
        rounded_cost = round(cost, 4)
        assert trace.cost == rounded_cost
        # Verify by converting to string and checking decimal places
        cost_str = f"{trace.cost:.4f}"
        decimal_part = cost_str.split(".")[1]
        assert len(decimal_part) <= 4
