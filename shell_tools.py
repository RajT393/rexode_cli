import subprocess

def run_shell_command(command: str) -> str:
    """Executes a shell command and returns its output.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The standard output and standard error of the command, or an error message.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

