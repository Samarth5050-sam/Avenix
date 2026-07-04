"""
Avenix Example: Using @trace with OpenAI API

This example demonstrates how to use the @trace decorator with OpenAI's API.
Avenix automatically captures timing, token usage, and costs, then displays
a beautifully formatted trace in your terminal.

To run this example, you need:
1. An OpenAI API key (set as OPENAI_API_KEY environment variable)
2. The openai package: pip install openai
3. Avenix installed: pip install avenix
"""

from avenix import trace
from unittest.mock import Mock

# For production use, uncomment and use real OpenAI client:
# from openai import OpenAI
# client = OpenAI()

# For this example, we'll use a mock to avoid requiring an API key


def create_mock_openai_response(model="gpt-4", prompt="What is AI?", response_text="AI is..."):
    """Create a mock OpenAI response for demonstration."""
    mock_response = Mock()
    mock_response.model = model
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 12  # "What is AI?" is roughly 5 tokens
    mock_response.usage.completion_tokens = 100  # "AI is..." response
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = response_text
    return mock_response


@trace
def query_gpt4(question: str) -> str:
    """
    Query GPT-4 with a question.
    
    The @trace decorator will automatically:
    - Measure execution time
    - Extract model, tokens, and response
    - Calculate cost based on token usage
    - Display formatted trace output
    
    Args:
        question: The question to ask GPT-4
        
    Returns:
        The response from GPT-4
    """
    # In production, this would call the real OpenAI API:
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": question}]
    # )
    # return response
    
    # For this example, we return a mock response:
    return create_mock_openai_response(
        model="gpt-4",
        prompt=question,
        response_text="Artificial Intelligence (AI) is the simulation of human intelligence "
                      "processes by machines, especially computer systems. These processes include "
                      "learning, reasoning, and self-correction."
    )


@trace
def query_gpt35_turbo(question: str) -> str:
    """
    Query GPT-3.5-turbo with a question.
    
    This is typically faster and cheaper than GPT-4.
    """
    return create_mock_openai_response(
        model="gpt-3.5-turbo",
        prompt=question,
        response_text="AI refers to computer systems designed to perform tasks that typically "
                      "require human intelligence. It includes learning, problem-solving, and "
                      "pattern recognition."
    )


def main():
    """Run the example."""
    print("\n" + "=" * 70)
    print("Avenix Example: OpenAI Integration")
    print("=" * 70 + "\n")
    
    # Example 1: Query GPT-4
    print("1. Querying GPT-4:")
    print("-" * 70)
    result1 = query_gpt4("What is artificial intelligence?")
    print(f"\nResponse: {result1.choices[0].message.content if hasattr(result1, 'choices') else result1}\n")
    
    # Example 2: Query GPT-3.5-turbo
    print("\n2. Querying GPT-3.5-turbo:")
    print("-" * 70)
    result2 = query_gpt35_turbo("Explain machine learning in simple terms.")
    print(f"\nResponse: {result2.choices[0].message.content if hasattr(result2, 'choices') else result2}\n")
    
    print("=" * 70)
    print("Notice how Avenix automatically captured and displayed:")
    print("  - Model name")
    print("  - Execution latency in seconds")
    print("  - Input and output token counts")
    print("  - Estimated cost in USD")
    print("  - Prompt and response text")
    print("=" * 70 + "\n")
    
    # Example 3: Multiple calls show independent traces
    print("\n3. Comparing responses:")
    print("-" * 70)
    result3 = query_gpt4("What are neural networks?")
    print(f"\nResponse: {result3.choices[0].message.content if hasattr(result3, 'choices') else result3}\n")
    
    print("\n" + "=" * 70)
    print("Each function call is traced independently.")
    print("You can use @trace on any function that returns an AI response.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
