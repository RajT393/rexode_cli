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
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from core.nl_executor import execute_nl_command
from core.os_commander import open_application, schedule_shutdown, abort_shutdown, gui_click
from core.tool_creator import build_new_tool
from file_tools import delete_file, move_file, copy_file, rename_item, create_directory, delete_directory, search_file_content, zip_item, unzip_item
from core.project_builder import generate_project_template, execute_code_snippet
from core.code_analyzer import analyze_code
from core.git_commander import git_clone, git_commit, git_push, git_status
from core.keyboard_automation import simulate_key_press, simulate_type

async def headless_search(query: str, num_results: int = 5):
    """
    Performs a web search using a headless browser and returns the top results.
    """
    results = []
    print(f"[DEBUG] HeadlessSearch: Querying for '{query}' using DDGS API.")
    try:
        with DDGS() as ddgs:
            api_results = ddgs.text(query, max_results=num_results)
            for r in api_results:
                results.append({"title": r['title'], "link": r['href']})
    except Exception as e:
        print(f"[DEBUG] HeadlessSearch Error during DDGS API search: {e}")
        return f"An error occurred during web search: {e}"

    # Fetch content for each link
    for result in results:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(result['link'], wait_until='networkidle')
                
                # Wait for the main content to be available
                await page.wait_for_selector('body', timeout=5000)
                
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract text from the body, removing script and style tags
                for s in soup(['script', 'style']):
                    s.decompose()
                
                content = ' '.join(soup.body.get_text().split())
                result['content'] = content[:2000] # Limit content length
                
        except Exception as e:
            print(f"[DEBUG] HeadlessSearch Error fetching content for {result.get('link', 'unknown')}: {e}")
            result['content'] = f"Could not fetch content: {e}"
        finally:
            await browser.close()

    print(f"[DEBUG] HeadlessSearch returning {len(results)} results.")
    return results

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
        print(f"Attempting to write to: {filename}")
        print(f"Content length: {len(content)}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}. Input received: '{text}'"

def list_directory(path=" .") -> str:
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
    "GetTime": (lambda _: get_current_time(), "Get the current date and time. No input required."),
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
    "HeadlessSearch": (headless_search, "Perform a headless web search. Input: a search query."),
    "ExecuteNLCommand": (execute_nl_command, "Execute a natural language command. Input: the command string."),
    "OpenApplication": (open_application, "Open a specified application. Input: the application name."),
    "ScheduleShutdown": (schedule_shutdown, "Schedule a system shutdown in N minutes. Input: number of minutes."),
    "AbortShutdown": (abort_shutdown, "Abort a pending system shutdown. No input required."),
    "GUIClick": (gui_click, "Perform a GUI click at specified X, Y coordinates. Input: X_coordinate,Y_coordinate."),
    "DeleteFile": (delete_file, "Delete a file from disk. Input: the file path."),
    "MoveFile": (move_file, "Move a file from source to destination. Input: source_path|||destination_path."),
    "CopyFile": (copy_file, "Copy a file from source to destination. Input: source_path|||destination_path."),
    "RenameItem": (rename_item, "Rename a file or directory. Input: old_path|||new_path."),
    "CreateDirectory": (create_directory, "Create a new directory. Input: the directory path."),
    "DeleteDirectory": (delete_directory, "Delete a directory. Input: the directory path."),
    "SearchFileContent": (search_file_content, "Search for content within files. Input: path|||pattern."),
    "BuildNewTool": (build_new_tool, "Generate and save a new Python tool from a natural language description. Input: the tool's description."),
    "AnalyzeCode": (analyze_code, "Analyze a code snippet or file content using the LLM. Input: code_content_or_filepath."),
    "GitClone": (lambda x: git_clone(*split_input(x)), "Clone a Git repository. Input: repository_url|||local_path."),
    "GitCommit": (git_commit, "Commit changes in the current Git repository. Input: commit_message."),
    "GitPush": (lambda _: git_push(), "Push committed changes to the remote Git repository. No input required."),
    "GitStatus": (lambda _: git_status(), "Show the status of the current Git repository. No input required."),
    "ListRunningApplications": (lambda _: list_running_applications(), "List all currently running applications."),
    "SimulateKeyPress": (simulate_key_press, "Simulate a single key press. Input: key_name (e.g., 'enter', 'esc', 'win')."),
    "SimulateType": (simulate_type, "Simulate typing a string of text. Input: text_to_type."),
    "ZipItem": (zip_item, "Compress a file or directory into a zip archive. Input: path_to_item|||output_filename.zip."),
    "UnzipItem": (unzip_item, "Extract a zip archive to a specified directory. Input: path_to_zip_file|||output_directory."),
}