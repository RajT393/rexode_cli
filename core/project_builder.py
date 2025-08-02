import os
import subprocess
from rich.console import Console

console = Console()

def generate_project_template(template_type: str, project_name: str) -> str:
    """Generates a basic project template (e.g., Python, HTML, Flask)."""
    template_type_lower = template_type.lower()
    
    if not project_name:
        return "Error: Project name cannot be empty."

    if os.path.exists(project_name):
        return f"Error: Directory '{project_name}' already exists."

    try:
        os.makedirs(project_name)
        if template_type_lower == "python":
            with open(os.path.join(project_name, "main.py"), "w") as f:
                f.write("print(\"Hello from Python project!\")")
            return f"✅ Python project '{project_name}' created with main.py."
        elif template_type_lower == "html":
            with open(os.path.join(project_name, "index.html"), "w") as f:
                f.write("<!DOCTYPE html>\n<html>\n<head><title>My HTML Project</title></head>\n<body><h1>Hello from HTML!</h1></body>\n</html>")
            return f"✅ HTML project '{project_name}' created with index.html."
        elif template_type_lower == "flask":
            with open(os.path.join(project_name, "app.py"), "w") as f:
                f.write("from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef hello():\n    return \"Hello from Flask!\"\nif __name__ == '__main__':\n    app.run(debug=True)")
            with open(os.path.join(project_name, "requirements.txt"), "w") as f:
                f.write("Flask")
            return f"✅ Flask project '{project_name}' created with app.py and requirements.txt."
        else:
            return f"Error: Unsupported template type '{template_type}'. Supported: python, html, flask."
    except Exception as e:
        return f"❌ Error generating project template: {str(e)}"

def execute_code_snippet(code: str, language: str) -> str:
    """Executes a code snippet in the specified language (Python, JavaScript, PowerShell)."""
    language_lower = language.lower()
    
    try:
        if language_lower == "python":
            result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        elif language_lower == "javascript":
            # Requires Node.js to be installed and in PATH
            result = subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True)
        elif language_lower == "powershell":
            result = subprocess.run(["powershell", "-Command", code], capture_output=True, text=True, check=True)
        else:
            return f"Error: Unsupported language '{language}'. Supported: python, javascript, powershell."

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        
        if not output:
            output = "Code executed successfully with no output."
        
        return output
    except FileNotFoundError:
        return f"Error: Interpreter for '{language}' not found. Please ensure it's installed and in your PATH."
    except subprocess.CalledProcessError as e:
        return f"Error executing code: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
