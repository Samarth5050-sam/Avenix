"""
Avenix Example: Using the Manual Tracer API

This example demonstrates how to use the Tracer.create_trace() method to
manually create and display traces. This is useful when you want explicit
control over all trace values, or when integrating with custom systems.

No external dependencies required - just Avenix!
"""

from avenix import Tracer
import time


def manual_trace_example_1():
    """Simple manual trace example."""
    tracer = Tracer()
    
    print("\n" + "=" * 70)
    print("Example 1: Simple Manual Trace")
    print("=" * 70 + "\n")
    
    # Manually create a trace with explicit values
    tracer.create_trace(
        model="gpt-4",
        latency=1.234,
        input_tokens=150,
        output_tokens=250,
        cost=0.0450,
        prompt="What are the benefits of machine learning?",
        response="Machine learning offers several key benefits:\n"
                "1. Automation of complex tasks\n"
                "2. Improved decision making\n"
                "3. Scalability\n"
                "4. Continuous improvement through learning"
    )
    
    print("\nIn this example, we explicitly specified:")
    print("  - Model: gpt-4")
    print("  - Latency: 1.234 seconds (automatically rounded to 1.23)")
    print("  - Input tokens: 150")
    print("  - Output tokens: 250")
    print("  - Cost: $0.0450 (automatically rounded to 4 decimals)")
    print()


def manual_trace_example_2():
    """Manual trace with simulated real-time measurement."""
    tracer = Tracer()
    
    print("\n" + "=" * 70)
    print("Example 2: Manual Trace with Simulated Timing")
    print("=" * 70 + "\n")
    
    # Simulate an API call with timing
    print("Simulating API call...", end="", flush=True)
    start_time = time.perf_counter()
    
    # Simulate processing
    time.sleep(0.5)
    
    end_time = time.perf_counter()
    latency = end_time - start_time
    
    print(f" completed in {latency:.3f} seconds\n")
    
    # Create trace with measured latency
    tracer.create_trace(
        model="claude-3-opus",
        latency=latency,
        input_tokens=200,
        output_tokens=350,
        cost=0.0675,
        prompt="Explain how neural networks work.",
        response="Neural networks are inspired by biological neural networks.\n"
                "They consist of interconnected nodes (neurons) organized in layers:\n"
                "1. Input layer: Receives data\n"
                "2. Hidden layers: Process information\n"
                "3. Output layer: Produces results\n"
                "These networks learn by adjusting connection weights through backpropagation."
    )
    
    print("Trace created with measured latency from time.perf_counter()")
    print()


def manual_trace_example_3():
    """Multiple traces showing cost comparison."""
    tracer = Tracer()
    
    print("\n" + "=" * 70)
    print("Example 3: Cost Comparison Across Models")
    print("=" * 70 + "\n")
    
    # Same prompt and response length across models to show cost differences
    prompt = "Write a comprehensive overview of quantum computing."
    response = ("Quantum computing represents a revolutionary paradigm in computation. "
                "Unlike classical computers that use bits, quantum computers use quantum bits (qubits) "
                "that can exist in superposition, processed based on quantum mechanical principles.")
    
    # Model 1: GPT-3.5-turbo (cheapest)
    print("1. GPT-3.5-turbo:")
    print("-" * 70)
    tracer.create_trace(
        model="gpt-3.5-turbo",
        latency=0.6,
        input_tokens=100,
        output_tokens=80,
        cost=0.0015,  # Calculate: (100/1000)*0.0005 + (80/1000)*0.0015
        prompt=prompt,
        response=response
    )
    
    # Model 2: GPT-4-turbo (moderate cost)
    print("\n2. GPT-4-turbo:")
    print("-" * 70)
    tracer.create_trace(
        model="gpt-4-turbo",
        latency=1.2,
        input_tokens=100,
        output_tokens=80,
        cost=0.0035,  # Calculate: (100/1000)*0.01 + (80/1000)*0.03
        prompt=prompt,
        response=response
    )
    
    # Model 3: Claude-3-opus (highest cost, typically most capable)
    print("\n3. Claude-3-opus:")
    print("-" * 70)
    tracer.create_trace(
        model="claude-3-opus",
        latency=1.5,
        input_tokens=100,
        output_tokens=80,
        cost=0.0042,  # Calculate: (100/1000)*0.015 + (80/1000)*0.075
        prompt=prompt,
        response=response
    )
    
    print("\nCost Comparison:")
    print("  GPT-3.5-turbo: $0.0015 (fastest, cheapest)")
    print("  GPT-4-turbo:   $0.0035 (balanced)")
    print("  Claude-3-opus: $0.0042 (most capable)")
    print()


def manual_trace_example_4():
    """Edge cases and precision demonstration."""
    tracer = Tracer()
    
    print("\n" + "=" * 70)
    print("Example 4: Precision and Validation Demonstration")
    print("=" * 70 + "\n")
    
    # Demonstrate precision rounding
    tracer.create_trace(
        model="gpt-4",
        latency=1.23456789,  # Will be rounded to 1.23
        input_tokens=999,
        output_tokens=1234,
        cost=0.012345678,  # Will be rounded to 0.0123
        prompt="Test prompt with various precisions",
        response="Response that demonstrates how Avenix handles precision."
    )
    
    print("Notice how:")
    print("  - Latency 1.23456789 was rounded to 1.23 (2 decimal places)")
    print("  - Cost 0.012345678 was rounded to 0.0123 (4 decimal places)")
    print("  - Token counts are always integers")
    print()


def main():
    """Run all manual trace examples."""
    print("\n" + "=" * 70)
    print("Avenix Manual Tracer API Examples")
    print("=" * 70)
    print("\nThese examples show how to use Tracer.create_trace()")
    print("to manually create and display traces without decorators.")
    print()
    
    manual_trace_example_1()
    manual_trace_example_2()
    manual_trace_example_3()
    manual_trace_example_4()
    
    print("=" * 70)
    print("Use Cases for Manual Tracing:")
    print("  - Custom integrations with proprietary AI services")
    print("  - Post-processing of API responses")
    print("  - Building dashboards that aggregate traces")
    print("  - Testing and development without real API calls")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
