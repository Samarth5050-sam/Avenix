# Terminal output formatting using rich library

from rich.panel import Panel
from rich.text import Text
from rich.console import RenderableType

from .models import TraceModel


class RichFormatter:
    """Formats traces using the rich library for beautiful terminal output."""
    
    def format(self, trace: TraceModel) -> RenderableType:
        """
        Format a trace model for terminal display.
        
        Creates a structured panel with:
        - Header with emoji and title
        - Metadata section (model, latency, tokens, cost)
        - Prompt section
        - Response section
        
        Args:
            trace: The trace model to format
            
        Returns:
            Rich renderable object (Panel)
        """
        # Build metadata section
        metadata = Text()
        metadata.append("Model:    ", style="bold cyan")
        metadata.append(f"{trace.model}\n")
        
        metadata.append("Latency:  ", style="bold cyan")
        metadata.append(f"{trace.latency:.2f}s\n")
        
        metadata.append("Input:    ", style="bold cyan")
        metadata.append(f"{trace.input_tokens} tokens\n")
        
        metadata.append("Output:   ", style="bold cyan")
        metadata.append(f"{trace.output_tokens} tokens\n")
        
        metadata.append("Cost:     ", style="bold cyan")
        metadata.append(f"${trace.cost:.4f}\n")
        
        # Build complete output
        output = Text()
        output.append(metadata)
        output.append("\n")
        
        # Prompt section
        output.append("━" * 50 + "\n", style="dim")
        output.append("Prompt\n", style="bold yellow")
        output.append("━" * 50 + "\n", style="dim")
        output.append(f"{trace.prompt}\n\n")
        
        # Response section
        output.append("━" * 50 + "\n", style="dim")
        output.append("Response\n", style="bold green")
        output.append("━" * 50 + "\n", style="dim")
        output.append(f"{trace.response}\n")
        
        # Wrap in panel with title
        panel = Panel(
            output,
            title="🚀 Avenix Trace",
            border_style="blue",
            padding=(1, 2)
        )
        
        return panel
