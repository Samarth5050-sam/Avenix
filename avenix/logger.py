# Terminal display logger

from rich.console import Console, RenderableType


class RichLogger:
    """Logs traces to terminal using rich library."""
    
    def __init__(self, console: Console = None):
        """
        Initialize logger with optional custom console.
        
        Args:
            console: Custom rich Console instance
        """
        self.console = console or Console()
    
    def log(self, renderable: RenderableType) -> None:
        """
        Display a formatted trace to the terminal.
        
        Args:
            renderable: Rich renderable object to display
        """
        try:
            self.console.print(renderable)
        except Exception as e:
            # Fallback to basic print if rich rendering fails
            print(f"[Avenix] Failed to render trace: {e}")
