import subprocess
from rich.console import Console

console = Console()

def list_running_applications() -> str:
    """Lists currently running applications on Windows."""
    try:
        # Using tasklist command to get process information
        result = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
        running_apps = []
        for line in lines:
            parts = line.split('","')
            if len(parts) > 0:
                app_name = parts[0].strip('"')
                running_apps.append(app_name)
        
        if running_apps:
            return "Currently running applications:\n" + "\n".join(running_apps)
        else:
            return "No applications appear to be running."

    except FileNotFoundError:
        return "❌ 'tasklist' command not found. This tool is only available on Windows."
    except Exception as e:
        return f"❌ An error occurred while listing applications: {e}"