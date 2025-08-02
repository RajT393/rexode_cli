import subprocess
from rich.console import Console

console = Console()

def execute_nl_command(command: str, confirm: bool = True):
    """
    Executes a shell command after optional user confirmation.
    """
    if not command:
        console.print("No command to execute.", style="bold red")
        return "No command to execute."

    console.print(f"Suggested command: [bold yellow]{command}[/bold yellow]")

    if confirm:
        # Check for potentially dangerous commands
        dangerous_commands = ["rm", "del", "shutdown", "reboot", "format", ":(){:|:&};:"]
        if any(cmd in command.lower() for cmd in dangerous_commands):
            console.print("This command may be dangerous.", style="bold red")
            confirm_input = console.input("Are you sure you want to execute? (y/n): ").lower()
            if confirm_input != 'y':
                console.print("Execution cancelled.", style="bold yellow")
                return "Execution cancelled."
        else:
            confirm_input = console.input("Execute this command? (y/n): ").lower()
            if confirm_input != 'y':
                console.print("Execution cancelled.", style="bold yellow")
                return "Execution cancelled."
    
    try:
        # Use powershell for better compatibility on Windows, especially for chained commands
        # Using -Command "& { ... }" ensures proper parsing of complex commands
        powershell_command = f"& {{ {command} }}"
        result = subprocess.run(["powershell", "-Command", powershell_command], capture_output=True, text=True, check=True, shell=True)
        
        output_str = ""
        if result.stdout:
            output_str += "[bold green]Output:[/bold green]\n"
            output_str += result.stdout
        if result.stderr:
            output_str += "[bold red]Errors:[/bold red]\n"
            output_str += result.stderr
        
        if not output_str:
            output_str = "Command executed successfully with no output."

        console.print(output_str)
        return output_str
            
    except subprocess.CalledProcessError as e:
        error_message = f"[bold red]An error occurred while executing the command:[/bold red]\n"
        error_message += f"[bold red]Return Code:[/bold red] {e.returncode}\n"
        if e.stdout:
            error_message += f"[bold green]Output:[/bold green]\n{e.stdout}\n"
        if e.stderr:
            error_message += f"[bold red]Errors:[/bold red]\n{e.stderr}"
        console.print(error_message)
        return error_message
    except FileNotFoundError:
        error_message = "'powershell' command not found. Please ensure PowerShell is installed and in your PATH."
        console.print(error_message, style="bold red")
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        console.print(error_message, style="bold red")
        return error_message