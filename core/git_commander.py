import subprocess
import os
from rich.console import Console

console = Console()

def run_git_command(command_args: list) -> str:
    """Helper to run git commands and capture output."""
    try:
        result = subprocess.run(["git"] + command_args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Git command failed: {e.stderr.strip()}"
    except FileNotFoundError:
        return "❌ Git is not installed or not in your system PATH."
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"

def git_clone(repo_url: str, local_path: str) -> str:
    """Clones a Git repository from a URL to a specified local path."""
    if os.path.exists(local_path):
        return f"❌ Local path '{local_path}' already exists. Please choose a different path or delete the existing one."
    console.print(f"Cloning '{repo_url}' into '{local_path}'...")
    return run_git_command(["clone", repo_url, local_path])

def git_commit(message: str) -> str:
    """Commits changes in the current Git repository."""
    console.print(f"Committing with message: '{message}'...")
    return run_git_command(["commit", "-am", message])

def git_push() -> str:
    """Pushes committed changes to the remote Git repository."""
    console.print("Pushing changes...")
    return run_git_command(["push"])

def git_status() -> str:
    """Shows the status of the current Git repository."""
    console.print("Checking Git status...")
    return run_git_command(["status"])
