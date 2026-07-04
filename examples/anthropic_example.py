"""
Avenix Example: Using @trace with Anthropic API

This example demonstrates how to use the @trace decorator with Anthropic's API.
Avenix automatically captures timing, token usage, and costs, then displays
a beautifully formatted trace in your terminal.

To run this example, you need:
1. An Anthropic API key (set as ANTHROPIC_API_KEY environment variable)
2. The anthropic package: pip install anthropic
3. Avenix installed: pip install avenix
"""

from avenix import trace
from unittest.mock import Mock

# For production use, uncomment and use real Anthropic client:
# from anthropic import Anthropic
# client = Anthropic()

# For this example, we'll use a mock to avoid requiring an API key


def create_mock_anthropic_response(model="claude-3-opus", prompt="What is AI?", response_text="AI is..."):
    """Create a mock Anthropic response for demonstration."""
    mock_response = Mock()
    mock_response.model = model
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 15  # "What is AI?" is roughly 5 tokens
    mock_response.usage.output_tokens = 120  # "AI is..." response
    mock_response.content = [Mock()]
    mock_response.content[0].text = response_text
    return mock_response


@trace
def query_claude_opus(question: str) -> str:
    """
    Query Claude 3 Opus with a question.
    
    Claude 3 Opus is the most capable Claude model, best for complex reasoning
    and analysis tasks.
    
    The @trace decorator will automatically:
    - Measure execution time
    - Extract model, tokens, and response
    - Calculate cost based on token usage
    - Display formatted trace output
    
    Args:
        question: The question to ask Claude
        
    Returns:
        The response from Claude
    """
    # In production, this would call the real Anthropic API:
    # response = client.messages.create(
    #     model="claude-3-opus-20240229",
    #     max_tokens=1024,
    #     messages=[
    #         {"role": "user", "content": question}
    #     ]
    # )
    # return response
    
    # For this example, we return a mock response:
    return create_mock_anthropic_response(
        model="claude-3-opus",
        prompt=question,
        response_text="Artificial Intelligence (AI) represents a paradigm shift in computing, "
                      "enabling machines to execute tasks that traditionally required human cognition. "
                      "AI systems leverage machine learning algorithms to extract patterns from data "
                      "and improve their performance iteratively."
    )


@trace
def query_claude_sonnet(question: str) -> str:
    """
    Query Claude 3 Sonnet with a question.
    
    Claude 3 Sonnet offers a good balance between capability and speed.
    """
    return create_mock_anthropic_response(
        model="claude-3-sonnet",
        prompt=question,
        response_text="AI, or Artificial Intelligence, is the development of computer systems capable "
                      "of performing tasks that normally need human intelligence. This includes visual "
                      "perception, language understanding, and decision making across various domains."
    )


@trace
def query_claude_haiku(question: str) -> str:
    """
    Query Claude 3 Haiku with a question.
    
    Claude 3 Haiku is the fastest and most compact Claude model, ideal for
    rapid inference and latency-sensitive applications.
    """
    return create_mock_anthropic_response(
        model="claude-3-haiku",
        prompt=question,
        response_text="AI refers to computer systems designed to perform intelligent tasks. "
                      "It learns from data and improves through experience."
    )


def main():
    """Run the example."""
    print("\n" + "=" * 70)
    print("Avenix Example: Anthropic Integration")
    print("=" * 70 + "\n")
    
    # Example 1: Query Claude 3 Opus
    print("1. Querying Claude 3 Opus (most capable):")
    print("-" * 70)
    result1 = query_claude_opus("What is artificial intelligence?")
    print(f"\nResponse: {result1.content[0].text if hasattr(result1, 'content') else result1}\n")
    
    # Example 2: Query Claude 3 Sonnet
    print("\n2. Querying Claude 3 Sonnet (balanced):")
    print("-" * 70)
    result2 = query_claude_sonnet("Explain machine learning.")
    print(f"\nResponse: {result2.content[0].text if hasattr(result2, 'content') else result2}\n")
    
    # Example 3: Query Claude 3 Haiku
    print("\n3. Querying Claude 3 Haiku (fastest):")
    print("-" * 70)
    result3 = query_claude_haiku("What is AI?")
    print(f"\nResponse: {result3.content[0].text if hasattr(result3, 'content') else result3}\n")
    
    print("=" * 70)
    print("Notice how Avenix captures and displays for each model:")
    print("  - Model name (Opus, Sonnet, or Haiku)")
    print("  - Execution latency")
    print("  - Token usage (input and output)")
    print("  - Estimated cost (Opus is most expensive, Haiku is most economical)")
    print("  - Complete prompt and response text")
    print("=" * 70 + "\n")
    
    # Demonstrate cost comparison
    print("\n4. Cost Comparison:")
    print("-" * 70)
    print("Haiku is typically the most cost-effective for simple queries")
    print("Sonnet offers balanced capability and speed")
    print("Opus provides the most sophisticated responses\n")
    
    print("=" * 70)
    print("Avenix helps you understand the performance and cost trade-offs")
    print("of different models and optimize your AI infrastructure.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
