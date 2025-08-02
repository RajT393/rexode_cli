from rich.console import Console

console = Console()

def analyze_code(code_input: str, llm) -> str:
    """
    Analyzes a given code snippet or file content using the LLM.
    The input can be a file path or the code content itself.
    """
    code_content = ""
    if os.path.exists(code_input):
        try:
            with open(code_input, 'r', encoding='utf-8') as f:
                code_content = f.read()
            console.print(f"Analyzing code from file: [bold green]{code_input}[/bold green]")
        except Exception as e:
            return f"Error reading file '{code_input}': {e}"
    else:
        code_content = code_input
        console.print("Analyzing provided code snippet.")

    if not code_content:
        return "No code provided for analysis."

    prompt = f"""
    You are an expert code analyzer. Analyze the following code and provide a concise explanation of its purpose, 
    its main functionalities, and any potential improvements or issues you identify. 
    If the code is incomplete or has syntax errors, point them out.

    Code:
    {code_content}

    Analysis:
    """
    
    try:
        analysis = llm.invoke(prompt).strip()
        return analysis
    except Exception as e:
        return f"Error during code analysis: {e}"
