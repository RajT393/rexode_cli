import time
import threading
import sys
from rich.console import Console
from rich.text import Text
from rich.spinner import Spinner
from theme import Theme

class LoadingSpinner:
    def __init__(self, console: Console, message: str = "Thinking..."):
        self.console = console
        self.message = message
        self._stop_event = threading.Event()
        self._thread = None
        self._start_time = 0
        self.spinner = Spinner("dots", style=Theme.ACTIVE_DOT)
        self.is_active = False

    def _animate(self):
        self._start_time = time.time()
        while not self._stop_event.is_set():
            elapsed_time = time.time() - self._start_time
            spinner_frame = self.spinner.render(elapsed_time)
            
            # Construct the full line to print
            line = Text.assemble(
                spinner_frame,
                " ",
                Text(self.message, style=Theme.HEADERS),
                Text(f" ({elapsed_time:.1f}s)", style=Theme.INACTIVE_DOT)
            )
            
            # Move cursor to the beginning of the line and clear it
            sys.stdout.write("\r" + " " * self.console.width)
            sys.stdout.write("\r" + line.plain)
            sys.stdout.flush()
            time.sleep(0.1) # Update every 100ms

    def start(self, message: str = None):
        if self.is_active: # Prevent starting if already active
            return
        if message:
            self.message = message
        self._stop_event.clear()
        self.is_active = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.is_active: # Prevent stopping if not active
            return
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2) # Give a short time for the thread to finish
        
        # Clear the spinner line after stopping
        sys.stdout.write("\r" + " " * self.console.width + "\r")
        sys.stdout.flush()
        self.is_active = False

# Example Usage (for testing)
if __name__ == "__main__":
    console = Console()
    spinner = LoadingSpinner(console, "Processing your request")
    
    console.print("Starting a simulated task...")
    spinner.start()
    time.sleep(3) # Simulate work
    spinner.stop()
    console.print("Task finished!")

    console.print("Starting another simulated task...")
    spinner.start("Fetching data from API")
    time.sleep(2) # Simulate work
    spinner.stop()
    console.print("Data fetched!")

    console.print("Done.")