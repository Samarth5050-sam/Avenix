# Provider-specific extraction logic for AI responses

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ResponseExtractor(ABC):
    """Abstract base class for AI response extractors."""
    
    @abstractmethod
    def can_extract(self, result: Any) -> bool:
        """Check if this extractor can handle the given result."""
        ...
    
    @abstractmethod
    def extract(self, result: Any) -> Dict[str, Any]:
        """Extract trace data from result."""
        ...


class OpenAIExtractor(ResponseExtractor):
    """Extractor for OpenAI response format."""
    
    def can_extract(self, result: Any) -> bool:
        """Check if result matches OpenAI format."""
        usage = getattr(result, 'usage', None)
        choices = getattr(result, 'choices', None)

        return (
            hasattr(result, 'model') and
            hasattr(usage, 'prompt_tokens') and
            hasattr(usage, 'completion_tokens') and
            isinstance(choices, (list, tuple))
        )
    
    def extract(self, result: Any) -> Dict[str, Any]:
        """Extract trace data from OpenAI response."""
        try:
            return {
                'model': result.model,
                'input_tokens': result.usage.prompt_tokens,
                'output_tokens': result.usage.completion_tokens,
                'prompt': '',  # Not available in response
                'response': result.choices[0].message.content
            }
        except (AttributeError, IndexError) as e:
            logger.warning(f"Failed to extract OpenAI trace data: {e}")
            return {}


class AnthropicExtractor(ResponseExtractor):
    """Extractor for Anthropic response format."""
    
    def can_extract(self, result: Any) -> bool:
        """Check if result matches Anthropic format."""
        usage = getattr(result, 'usage', None)
        content = getattr(result, 'content', None)

        return (
            hasattr(result, 'model') and
            hasattr(usage, 'input_tokens') and
            hasattr(usage, 'output_tokens') and
            isinstance(content, (list, tuple))
        )
    
    def extract(self, result: Any) -> Dict[str, Any]:
        """Extract trace data from Anthropic response."""
        try:
            return {
                'model': result.model,
                'input_tokens': result.usage.input_tokens,
                'output_tokens': result.usage.output_tokens,
                'prompt': '',  # Not available in response
                'response': result.content[0].text if result.content else ''
            }
        except (AttributeError, IndexError) as e:
            logger.warning(f"Failed to extract Anthropic trace data: {e}")
            return {}
