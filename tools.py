import os
import webbrowser
from datetime import datetime
from duckduckgo_search import DDGS
from timed_tasks import (
    remind_task,
    schedule_whatsapp_msg,
    pause_video_later,
    next_video_later,
)
from ocr_reader import capture_and_ocr
from utils import split_input, get_mode_config

# Tool functions
def search_web(query: str) -> str:
    """Searches the web using DuckDuckGo and returns the top 3 results."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            return "\n\n".join([f"{r['title']}\n{r['href']}" for r in results])
    except Exception as e:
        return f"Web search error: {str(e)}"

def read_file(path: str) -> str:
    """Reads the entire content of a file from the specified path."""
    try:
        if not os.path.exists(path): return "File not found."
        return open(path, "r", encoding="utf-8").read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(text: str) -> str:
    """Writes content to a file. The first part of the input before '|||' is the filename and the rest is the content."""
    try:
        filename, content = split_input(text)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return "Error. Use format: filename.txt ||| content"

def list_directory(path=".") -> str:
    """Lists the contents of a specified directory."""
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def open_url(url: str) -> str:
    """Opens a given URL in the default web browser."""
    try:
        webbrowser.open(url)
        return f"Successfully opened {url}"
    except Exception as e:
        return f"Error opening URL: {e}"

def switch_mode(mode: str) -> str:
    """Switches the assistant's operating mode. Available modes: power, eco, balanced."""
    config = get_mode_config(mode.lower())
    if config:
        return f"Switched to {mode} mode.\nFeatures: {config['features']}\nSpeed: {config['speed']}"
    else:
        return "Invalid mode. Choose from: power, eco, balanced."

# Tool dictionary
tools = {
    "GetTime": (get_current_time, "Get the current date and time. No input required."),
    "OpenWebURL": (open_url, "Open a website URL in the default browser. Input: a valid URL."),
    "SearchWeb": (search_web, "Search the web for a query. Input: a search query."),
    "ReadFile": (read_file, "Read a file from disk. Input: a valid file path."),
    "WriteFile": (write_file, "Write content to a file. Input format: filename.txt ||| content."),
    "ListDir": (list_directory, "List directory contents. Input: a valid directory path."),
    "RemindUser": (lambda x: remind_task("|||".join(split_input(x))), "Set a reminder. Format: task|||HH:MM"),
    "WhatsAppLater": (lambda x: schedule_whatsapp_msg(*split_input(x)), "Send WhatsApp message. Format: +91XXXXXXXXXX|||message|||HH:MM"),
    "PauseVideoLater": (lambda x: pause_video_later(int(x)), "Pause the video after N seconds."),
    "NextVideoLater": (lambda x: next_video_later(int(x)), "Play next video after N seconds."),
    "CaptureScreenText": (lambda _: capture_and_ocr(), "Read text from screen using OCR. No input required."),
    "SwitchMode": (switch_mode, "Switch assistant mode. Options: power, balanced, eco."),
}
