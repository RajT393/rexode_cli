import os

def read_file(path: str) -> str:
    try:
        if not os.path.exists(path):
            return "⚠️ File not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def write_file(text: str) -> str:
    try:
        filename, content = text.split("|||", 1)
        with open(filename.strip(), "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Wrote to {filename.strip()}"
    except Exception as e:
        return f"❌ Error writing to file: {str(e)}"


def list_directory(path: str = ".") -> str:
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"


def summarize_file(path: str) -> str:
    try:
        content = read_file(path)
        return content[:1000] + ("..." if len(content) > 1000 else "")
    except Exception as e:
        return f"❌ Could not summarize file: {str(e)}"
