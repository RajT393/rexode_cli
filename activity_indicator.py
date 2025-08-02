import time
import threading
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner
from theme import Theme

class ActivityIndicator:
    def __init__(self, console: Console, message: str = "Processing..."):
        self.console = console
        self.message = message
        self._stop_event = threading.Event()
        self._thread = None
        self._live = None
        self._start_time = 0
        self.spinner = Spinner("dots", style=Theme.ACTIVE_DOT)

    def _update_display(self):
        while not self._stop_event.is_set():
            elapsed_time = time.time() - self._start_time
            display_text = Text.assemble(
                self.spinner.render(elapsed_time), # Pass elapsed_time here
                " ",
                Text(self.message, style=Theme.HEADERS),
                Text(f" ({elapsed_time:.1f}s)", style=Theme.INACTIVE_DOT)
            )
            self._live.update(display_text)
            time.sleep(0.1) # Update every 100ms

    def start(self, message: str = None):
        if message:
            self.message = message
        self._stop_event.clear()
        self._start_time = time.time()
        self._live = Live(self.spinner.render(0), console=self.console, screen=True, refresh_per_second=10) # Pass 0 for initial render
        self._thread = threading.Thread(target=self._update_display, daemon=True)
        self._live.start()
        self._thread.start()

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=0.5) # Give a short time for the thread to finish
        if self._live:
            self._live.stop()

# Example Usage (for testing)
if __name__ == "__main__":
    console = Console()
    indicator = ActivityIndicator(console, "Resolving Package Installation")
    
    try:
        indicator.start()
        time.sleep(5) # Simulate work
    finally:
        indicator.stop()
    
    console.print("Task completed!")