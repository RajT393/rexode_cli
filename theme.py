from rich.console import Console
from rich.style import Style

console = Console()

class Theme:
    HEADERS = Style(color="#00B7C2")  # Cyan Bright
    ACTIVE_DOT = Style(color="#66B2FF")  # Blue Bright
    SUCCESS = Style(color="#70D88F")  # Green Bright
    ERROR = Style(color="#FF6B6B")  # Red Bright
    INACTIVE_DOT = Style(color="#B0B0B0")  # Gray
    PROGRESS_BAR = Style(color="#009EFF")  # Cool Blue
    LOG_PATH = Style(color="#A9A9A9")  # Light Gray
    RUNNING_INDICATOR = Style(color="yellow") # For '⧗'
    CHECK_MARK = Style(color="green") # For '✓'
    WARNING_MARK = Style(color="yellow") # For '⚠'
    ERROR_MARK = Style(color="red") # For '✘'
