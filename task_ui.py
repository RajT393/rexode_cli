import time
import threading
import sys
from rich.console import Console
from rich.live import Live
from rich.text import Text
from theme import Theme

class TaskUI:
    def __init__(self, steps):
        self.console = Console()
        self.steps = steps
        self.current_step_index = -1
        self.blinking_state = True
        self.stop_blinking_event = threading.Event()
        self.blinking_thread = None
        self.live_display = Live(self._get_progress_text(), console=self.console, screen=True, refresh_per_second=4, auto_refresh=False)

    def _blinking_animation(self):
        while not self.stop_blinking_event.is_set():
            self.blinking_state = not self.blinking_state
            if self.live_display:
                self.live_display.refresh()
            time.sleep(0.5) # Blink every 0.5 seconds

    def _get_progress_text(self):
        dots = []
        for i in range(len(self.steps)):
            if i == self.current_step_index:
                dot = "●" if self.blinking_state else "○"
                dots.append(Text(dot, style=Theme.ACTIVE_DOT))
            elif i < self.current_step_index:
                dots.append(Text("●", style=Theme.ACTIVE_DOT)) # Completed steps are solid
            else:
                dots.append(Text("○", style=Theme.INACTIVE_DOT))
        
        progress_str = " ".join(dot.plain for dot in dots) # Use plain text for joining
        
        return Text.assemble(
            "Progress: ",
            Text(progress_str),
            f"   (Step {self.current_step_index + 1}/{len(self.steps)})"
        )

    def start_task(self):
        self.console.print(Text(f"Task: {self.steps[0]}", style=Theme.HEADERS)) # Assuming first step is task title
        self.blinking_thread = threading.Thread(target=self._blinking_animation, daemon=True)
        self.blinking_thread.start()

    def start_live_display(self):
        self.live_display.start()

    def stop_live_display(self):
        self.live_display.stop()

    def start_step(self, step_index):
        self.current_step_index = step_index
        if self.live_display:
            self.live_display.update(self._get_progress_text())
        self.console.print(Text(f"⧗ Step {step_index + 1}: {self.steps[step_index]}", style=Theme.RUNNING_INDICATOR))

    def update_step_message(self, message):
        self.console.print(Text(f"    → {message}"))

    def complete_step(self, message="Completed"):
        if self.live_display:
            self.live_display.update(self._get_progress_text()) # Update to solid dot
        self.console.print(Text(f"    ✓ {message}", style=Theme.SUCCESS))

    def fail_step(self, message="Failed"):
        if self.live_display:
            self.live_display.update(self._get_progress_text()) # Update to solid dot
        self.console.print(Text(f"    ✘ {message}", style=Theme.ERROR))

    def end_task(self, total_time, log_path):
        if self.live_display:
            self.live_display.stop()
        self.stop_blinking_event.set()
        self.console.print(Text(f"✓ All tasks completed in {total_time:.1f} seconds.", style=Theme.SUCCESS))
        self.console.print(Text(f"Log: {log_path}", style=Theme.LOG_PATH))

# Example Usage (for testing)
if __name__ == "__main__":
    steps = [
        "Download and Launch Chromium",
        "Verifying Playwright installation",
        "Installing dependencies",
        "Downloading Chromium (123.1 MB)",
        "Launching Chromium"
    ]
    
    ui = TaskUI(steps)
    ui.start_task()
    ui.start_live_display()
    
    time.sleep(2)
    ui.start_step(0)
    ui.update_step_message("Checking system for existing install...")
    time.sleep(1)
    ui.complete_step("Found: Playwright v1.43.1")
    
    time.sleep(2)
    ui.start_step(1)
    ui.update_step_message("Running: npm install playwright-core")
    time.sleep(1)
    ui.update_step_message("Progress: [====>              ]  41s elapsed")
    time.sleep(1)
    ui.complete_step("Installed successfully")

    time.sleep(2)
    ui.start_step(2)
    ui.update_step_message("Downloaded: 73% (90.3MB @ 13.1MB/s)")
    time.sleep(1)
    ui.complete_step("Completed in 23.2s")

    time.sleep(2)
    ui.start_step(3)
    ui.complete_step("Chrome launched successfully")

    ui.stop_live_display()
    ui.end_task(91.3, ".rexode/logs/task_0728_1043.log")
    
    time.sleep(5) # Keep the script alive to see the final output