"""
Avenix - Python tracing library for AI requests.

Provides decorator-based tracing for AI/LLM requests with beautiful terminal output.
"""

from .decorator import trace
from .tracer import Tracer

__version__ = "0.1.0"
__all__ = ["trace", "Tracer"]
