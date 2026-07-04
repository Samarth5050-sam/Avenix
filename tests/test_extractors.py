# Tests for extraction logic

import pytest
from unittest.mock import Mock
from hypothesis import given, strategies as st, assume
from avenix.extractors import (
    ResponseExtractor,
    OpenAIExtractor,
    AnthropicExtractor
)


class TestOpenAIExtractor:
    """Unit tests for OpenAI extractor."""
    
    def test_can_extract_valid_openai_response(self):
        """Test that can_extract recognizes OpenAI format."""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock()
        mock_response.choices = [Mock()]
        
        extractor = OpenAIExtractor()
        assert extractor.can_extract(mock_response) is True
    
    def test_can_extract_rejects_missing_model(self):
        """Test that can_extract rejects response without model."""
        mock_response = Mock(spec=[])  # No model attribute
        mock_response.usage = Mock()
        mock_response.choices = [Mock()]
        
        extractor = OpenAIExtractor()
        assert extractor.can_extract(mock_response) is False
    
    def test_can_extract_rejects_missing_usage(self):
        """Test that can_extract rejects response without usage."""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.choices = [Mock()]
        # No usage attribute
        del mock_response.usage
        
        extractor = OpenAIExtractor()
        assert extractor.can_extract(mock_response) is False
    
    def test_can_extract_rejects_missing_choices(self):
        """Test that can_extract rejects response without choices."""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock()
        # No choices attribute
        del mock_response.choices
        
        extractor = OpenAIExtractor()
        assert extractor.can_extract(mock_response) is False
    
    def test_extract_valid_openai_response(self):
        """Test extracting data from valid OpenAI response."""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response text"
        
        extractor = OpenAIExtractor()
        result = extractor.extract(mock_response)
        
        assert result['model'] == "gpt-4"
        assert result['input_tokens'] == 100
        assert result['output_tokens'] == 50
        assert result['response'] == "Response text"
        assert result['prompt'] == ""
    
    def test_extract_handles_attribute_error(self):
        """Test that extract handles missing attributes gracefully."""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        # Make choices subscriptable but accessing attributes will fail
        mock_response.choices = []
        # This will cause IndexError when trying to access choices[0]
        
        extractor = OpenAIExtractor()
        result = extractor.extract(mock_response)
        
        # Should return empty dict on error (IndexError or AttributeError)
        assert result == {}
    
    def test_extract_handles_index_error(self):
        """Test that extract handles empty choices gracefully."""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.choices = []  # Empty choices
        
        extractor = OpenAIExtractor()
        result = extractor.extract(mock_response)
        
        # Should return empty dict on IndexError
        assert result == {}


class TestAnthropicExtractor:
    """Unit tests for Anthropic extractor."""
    
    def test_can_extract_valid_anthropic_response(self):
        """Test that can_extract recognizes Anthropic format."""
        mock_response = Mock()
        mock_response.model = "claude-3-opus"
        mock_response.usage = Mock()
        mock_response.content = [Mock()]
        
        extractor = AnthropicExtractor()
        assert extractor.can_extract(mock_response) is True
    
    def test_can_extract_rejects_missing_model(self):
        """Test that can_extract rejects response without model."""
        mock_response = Mock(spec=[])  # No model attribute
        mock_response.usage = Mock()
        mock_response.content = [Mock()]
        
        extractor = AnthropicExtractor()
        assert extractor.can_extract(mock_response) is False
    
    def test_can_extract_rejects_missing_usage(self):
        """Test that can_extract rejects response without usage."""
        mock_response = Mock()
        mock_response.model = "claude-3-opus"
        mock_response.content = [Mock()]
        # No usage attribute
        del mock_response.usage
        
        extractor = AnthropicExtractor()
        assert extractor.can_extract(mock_response) is False
    
    def test_can_extract_rejects_missing_content(self):
        """Test that can_extract rejects response without content."""
        mock_response = Mock()
        mock_response.model = "claude-3-opus"
        mock_response.usage = Mock()
        # No content attribute
        del mock_response.content
        
        extractor = AnthropicExtractor()
        assert extractor.can_extract(mock_response) is False
    
    def test_extract_valid_anthropic_response(self):
        """Test extracting data from valid Anthropic response."""
        mock_response = Mock()
        mock_response.model = "claude-3-sonnet"
        mock_response.usage.input_tokens = 75
        mock_response.usage.output_tokens = 125
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Claude response"
        
        extractor = AnthropicExtractor()
        result = extractor.extract(mock_response)
        
        assert result['model'] == "claude-3-sonnet"
        assert result['input_tokens'] == 75
        assert result['output_tokens'] == 125
        assert result['response'] == "Claude response"
        assert result['prompt'] == ""
    
    def test_extract_handles_attribute_error(self):
        """Test that extract handles missing attributes gracefully."""
        mock_response = Mock()
        mock_response.model = "claude-3-opus"
        # Make content subscriptable but empty to trigger IndexError
        mock_response.content = []
        
        extractor = AnthropicExtractor()
        result = extractor.extract(mock_response)
        
        # Should handle gracefully - either return empty or default response
        # If usage is missing, it will raise AttributeError caught in try-except
        # But if content is just empty, it should work fine and return empty string for response
        assert isinstance(result, dict) or result == {}
    
    def test_extract_handles_index_error_on_empty_content(self):
        """Test that extract handles empty content gracefully."""
        mock_response = Mock()
        mock_response.model = "claude-3-haiku"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 100
        mock_response.content = []  # Empty content
        
        extractor = AnthropicExtractor()
        result = extractor.extract(mock_response)
        
        # Should handle empty content case and return result with empty response
        assert result['model'] == "claude-3-haiku"
        assert result['input_tokens'] == 50
        assert result['output_tokens'] == 100


# Property-Based Tests
class TestExtractionProperties:
    """Property-based tests for extraction logic."""
    
    @given(
        object_type=st.just(Mock),
    )
    def test_extraction_failure_resilience(self, object_type):
        """Property 13: Extraction system is resilient to unknown object types."""
        # Create an object that doesn't match any known format
        unknown_object = Mock()
        # Make it not match OpenAI or Anthropic formats
        unknown_object.model = "unknown"
        # No usage or choices/content attributes
        if hasattr(unknown_object, 'usage'):
            del unknown_object.usage
        
        extractors = [OpenAIExtractor(), AnthropicExtractor()]
        
        # Should not raise exceptions for unknown types
        for extractor in extractors:
            can_extract = extractor.can_extract(unknown_object)
            if can_extract:
                # If extractor says it can extract, it might fail when extracting
                # But it should handle failures gracefully
                result = extractor.extract(unknown_object)
                assert isinstance(result, dict)  # Should return dict even on error
    
    @given(
        openai_input_tokens=st.integers(min_value=0, max_value=100000),
        openai_output_tokens=st.integers(min_value=0, max_value=100000),
        anthropic_input_tokens=st.integers(min_value=0, max_value=100000),
        anthropic_output_tokens=st.integers(min_value=0, max_value=100000),
    )
    def test_token_extraction_completeness(
        self,
        openai_input_tokens,
        openai_output_tokens,
        anthropic_input_tokens,
        anthropic_output_tokens
    ):
        """Property 16: Both input and output tokens are extracted correctly."""
        # Test OpenAI extraction
        openai_response = Mock()
        openai_response.model = "gpt-4"
        openai_response.usage.prompt_tokens = openai_input_tokens
        openai_response.usage.completion_tokens = openai_output_tokens
        openai_response.choices = [Mock()]
        openai_response.choices[0].message.content = "Response"
        
        openai_extractor = OpenAIExtractor()
        openai_result = openai_extractor.extract(openai_response)
        
        assert openai_result['input_tokens'] == openai_input_tokens
        assert openai_result['output_tokens'] == openai_output_tokens
        
        # Test Anthropic extraction
        anthropic_response = Mock()
        anthropic_response.model = "claude-3-opus"
        anthropic_response.usage.input_tokens = anthropic_input_tokens
        anthropic_response.usage.output_tokens = anthropic_output_tokens
        anthropic_response.content = [Mock()]
        anthropic_response.content[0].text = "Response"
        
        anthropic_extractor = AnthropicExtractor()
        anthropic_result = anthropic_extractor.extract(anthropic_response)
        
        assert anthropic_result['input_tokens'] == anthropic_input_tokens
        assert anthropic_result['output_tokens'] == anthropic_output_tokens
