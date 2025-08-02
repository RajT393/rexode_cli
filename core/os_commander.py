import os
import subprocess
import pyautogui
from rich.console import Console

console = Console()

def open_application(app_name: str):
    """Opens an application using the start command on Windows."""
    app_name_lower = app_name.lower()
    
    # Common applications mapping
    app_map = {
        "notepad": "notepad.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "calculator": "calc.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "settings": "ms-settings:", # Special URI for Windows Settings
        "explorer": "explorer.exe",
        "paint": "mspaint.exe",
        "wordpad": "write.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "whatsapp": "whatsapp:", # UWP app URI
        "instagram": "instagram:", # UWP app URI
    }

    target_app = app_map.get(app_name_lower, app_name) # Use mapped name or original

    try:
        if target_app.endswith(":"):
            # Handle URI schemes for UWP apps or settings
            try:
                subprocess.run(['start', '', target_app], shell=True, check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == 1 and "The system cannot find the file specified." in e.stderr:
                    error_message = f"Error opening application '{app_name}': The application URI '{target_app}' was not found. This might mean the UWP app is not installed or registered correctly."
                else:
                    error_message = f"Error opening application '{app_name}' via URI '{target_app}': {e.stderr}"
                console.print(f"[bold red]{error_message}[/bold red]")
                return error_message
        else:
            # Standard executable or file
            try:
                subprocess.run(['start', target_app], shell=True, check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == 1 and "The system cannot find the file specified." in e.stderr:
                    error_message = f"Error opening application '{app_name}': The executable '{target_app}' was not found in your PATH or the specified location."
                else:
                    error_message = f"Error opening application '{app_name}' via executable '{target_app}': {e.stderr}"
                console.print(f"[bold red]{error_message}[/bold red]")
                return error_message
        console.print(f"Attempting to open '[bold green]{app_name}[/bold green]'.")
        return f"Successfully sent command to open {app_name}."
    except Exception as e:
        error_message = f"An unexpected error occurred while trying to open '{app_name}': {e}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message

def schedule_shutdown(minutes: str):
    """Schedules a system shutdown on Windows."""
    try:
        minutes = int(minutes)
        seconds = minutes * 60
        
        # Display a confirmation prompt
        confirm = console.input(f"Are you sure you want to schedule a shutdown in [bold yellow]{minutes}[/bold yellow] minute(s)? (y/n): ").lower()
        if confirm != 'y':
            console.print("Shutdown cancelled.", style="bold yellow")
            return "Shutdown cancelled by user."

        # The /t flag specifies the time-out period in seconds.
        command = ['shutdown', '/s', '/t', str(seconds)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        message = f"System shutdown scheduled in {minutes} minute(s)."
        console.print(f"[bold green]{message}[/bold green]")
        console.print("To cancel the shutdown, run: [bold yellow]rexode os abort-shutdown[/bold yellow]")
        return message
    except ValueError:
        error_message = "Invalid time specified. Please provide a number of minutes."
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message
    except subprocess.CalledProcessError as e:
        error_message = f"Error scheduling shutdown: {e.stderr}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message

def abort_shutdown():
    """Cancels a pending system shutdown on Windows."""
    try:
        # The /a flag aborts a system shutdown.
        subprocess.run(['shutdown', '/a'], check=True, capture_output=True, text=True)
        message = "Shutdown has been cancelled."
        console.print(f"[bold green]{message}[/bold green]")
        return message
    except subprocess.CalledProcessError as e:
        # A non-zero exit code can mean there was no shutdown to abort.
        error_message = f"Could not abort shutdown. It might be because a shutdown was not scheduled. Details: {e.stderr}"
        console.print(f"[bold yellow]{error_message}[/bold yellow]")
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message

def gui_click(x_str: str, y_str: str):
    """Moves the mouse and clicks at the specified screen coordinates."""
    try:
        x = int(x_str)
        y = int(y_str)
        pyautogui.click(x, y)
        message = f"Clicked at coordinates ({x}, {y})."
        console.print(f"[bold green]{message}[/bold green]")
        return message
    except ValueError:
        error_message = "Invalid coordinates. Please provide integer values for x and y."
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message
    except Exception as e:
        error_message = f"An error occurred during the GUI click: {e}"
        console.print(f"[bold red]{error_message}[/bold red]")
        return error_message
