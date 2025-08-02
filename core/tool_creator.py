import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()
GENERATED_TOOLS_DIR = "generated_tools"

def generate_tool_code(instruction: str, llm):
    """Uses the LLM to generate Python code for a new tool."""
    prompt = f"""
    You are an expert Python developer. Your task is to generate a complete, standalone Python script based on the user's instruction. 
    The script should be well-commented, include necessary imports, and have a clear `if __name__ == '__main__':` block to make it executable.
    The code should not have any placeholders; it must be ready to run.
    Do not wrap the code in ```python or any other formatting.

    Instruction: 'Make a CLI tool that takes a folder path and counts the number of files in it.'

    Code:
    import os
    import sys

    def count_files_in_folder(folder_path):
        # Check if the path exists and is a directory
        if not os.path.isdir(folder_path):
            print(f"Error: '{folder_path}' is not a valid directory.")
            return 0
        
        file_count = 0
        for _, _, files in os.walk(folder_path):
            file_count += len(files)
        return file_count

    if __name__ == '__main__':
        if len(sys.argv) != 2:
            print("Usage: python <script_name>.py <folder_path>")
            sys.exit(1)
        
        path = sys.argv[1]
        count = count_files_in_folder(path)
        if count > 0:
            print(f"Total number of files in '{path}': {count}")
    # End of generated code

    Instruction: '{instruction}'

    Code:
    """
    
    try:
        code = llm.invoke(prompt).strip()
        # A simple cleanup to remove markdown, just in case
        if code.startswith("```python"):
            code = code.replace("```python", "", 1)
            code = code.rsplit("```", 1)[0]
        return code
    except Exception as e:
        return f"Error generating tool code: {e}"

def build_new_tool(instruction: str, llm):
    """Builds and saves a new tool from a natural language description."""
    console.print(f"\nBuilding tool for: '[italic yellow]{instruction}[/italic yellow]'", style="bold green")

    console.print("Generating code...", style="cyan")
    generated_code = generate_tool_code(instruction, llm)

    if "Error generating tool code" in generated_code:
        console.print(Panel(generated_code, title="Error", border_style="red"))
        return

    console.print(Panel(Syntax(generated_code, "python", theme="dracula", line_numbers=True), title="Generated Code", border_style="green"))

    confirm = console.input("Save this tool? (y/n): ").lower()
    if confirm != 'y':
        console.print("Tool creation cancelled.", style="bold yellow")
        return

    tool_name = console.input("Enter a filename for the new tool (e.g., my_tool.py): ").strip()
    if not tool_name.endswith(".py"):
        tool_name += ".py"

    if not os.path.exists(GENERATED_TOOLS_DIR):
        os.makedirs(GENERATED_TOOLS_DIR)

    file_path = os.path.join(GENERATED_TOOLS_DIR, tool_name)
    
    try:
        with open(file_path, "w") as f:
            f.write(generated_code)
        console.print(f"Tool '[bold green]{tool_name}[/bold green]' saved successfully in '{GENERATED_TOOLS_DIR}'.", style="bold green")
        console.print(f"You can run it using: [bold cyan]python {file_path}[/bold cyan]", style="bold green")
    except Exception as e:
        console.print(f"Error saving tool: {e}", style="bold red")
