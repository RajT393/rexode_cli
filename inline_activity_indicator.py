import time
import threading
import sys
from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.live import Live # Import Live
from theme import Theme

class InlineActivityIndicator:
    def __init__(self, console: Console, message: str = "Processing..."):
        self.console = console
        self.message = message
        self._stop_event = threading.Event()
        self._thread = None
        self._start_time = 0
        self.is_active = False
        self._live_display = None # To hold the Live context manager
        self._current_stream_content = "" # To hold streamed content

    def _get_display_text(self):
        elapsed_time = time.time() - self._start_time
        
        # Progressive dot animation
        num_dots = int(time.time() * 2) % 3 + 1 # 1, 2, or 3 dots
        dots_str = "●" * num_dots + "○" * (3 - num_dots)
        
        display_dots = Text(dots_str, style=Theme.ACTIVE_DOT)

        # Construct the full line to print
        line = Text.assemble(
            display_dots,
            " ",
            Text(self.message, style=Theme.HEADERS),
            Text(f" (esc to cancel, {elapsed_time:.0f}s)", style=Theme.INACTIVE_DOT),
            Text(f" {self._current_stream_content}") # Append streamed content
        )
        return line

    def _animate(self):
        self._start_time = time.time()
        with Live(self._get_display_text(), console=self.console, screen=False, refresh_per_second=10) as live:
            self._live_display = live
            while not self._stop_event.is_set():
                live.update(self._get_display_text())
                time.sleep(0.1) # Update every 100ms

    def start(self, message: str = None):
        if self.is_active: # Prevent starting if already active
            return
        if message:
            self.message = message
        self._stop_event.clear()
        self.is_active = True
        self._current_stream_content = "" # Reset streamed content on start
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def update_message(self, new_content: str):
        self._current_stream_content += new_content
        if self._live_display:
            self._live_display.update(self._get_display_text())

    def stop(self):
        if not self.is_active: # Prevent stopping if not active
            return
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2) # Give a short time for the thread to finish
        
        # Live context manager handles clearing, but ensure it's stopped
        if self._live_display:
            self._live_display.stop()
        self.is_active = False

# Example Usage (for testing)
if __name__ == "__main__":
    console = Console()
    indicator = InlineActivityIndicator(console, "Troubleshooting Rendering Sequence")
    
    console.print("Starting a simulated task...")
    indicator.start()
    time.sleep(1)
    indicator.update_message("Hello")
    time.sleep(1)
    indicator.update_message(" World!")
    time.sleep(3) # Simulate work
    indicator.stop()
    console.print("Task finished!")

    console.print("Starting another simulated task...")
    indicator.start("Fetching data from API")
    time.sleep(2) # Simulate work
    indicator.stop()
    console.print("Data fetched!")

    console.print("Done.")