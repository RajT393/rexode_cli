import os
import sys
import signal
import threading
import time
import asyncio
from pynput import keyboard
from datetime import datetime
from banner import print_banner
from mode_manager import load_mode, save_mode, get_mode_config
from voice_listener import get_voice_input
from permissions import ask_permission, save_permissions, load_permissions
from chat_logger import ensure_log_folder, get_today_log_path, append_chat
from shortcut_handler import listen_for_shortcuts
from popup_manager import show_confirmation
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from subscription import (
    load_subscription,
    is_subscription_active,
    enforce_subscription,
    activate_trial
)
from llm_handler import get_llm
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from tools import tools
from rich.console import Console
from rich.panel import Panel
from inline_activity_indicator import InlineActivityIndicator
from langchain.callbacks.base import BaseCallbackHandler
from task_ui import TaskUI

# Globals
exit_confirmed = False
chat_mode = "text"
permissions = {}
chat_history_path = ""
subscription_data = {}
mode_config = {}
llm = None
model_name = ""
cancel_event = threading.Event()
should_exit = False # New global flag for graceful exit

def on_press(key):
    try:
        if key == keyboard.Key.esc:
            print("ESC key pressed!") # Debug print
            cancel_event.set()
            return False # Stop listener
    except AttributeError:
        pass # Handle special keys that don't have a .char attribute

class CustomAgentCallbackHandler(BaseCallbackHandler):
    def __init__(self, indicator: InlineActivityIndicator):
        self.indicator = indicator

    def on_tool_start(self, tool: dict, input_str: str, **kwargs) -> None:
        self.indicator.start(f"Using tool: {tool.name}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        self.indicator.start("Agent thinking...") # Revert to thinking after tool ends

    def on_agent_action(self, action: dict, **kwargs) -> None:
        self.indicator.start(f"Agent thought: {action.log.strip()}")

    def on_agent_finish(self, finish: dict, **kwargs) -> None:
        self.indicator.stop()

def graceful_exit(sig, frame):
    global exit_confirmed, should_exit
    if exit_confirmed:
        print("\nExiting Rexode CLI.")
        should_exit = True # Set flag instead of sys.exit(0)
    else:
        print("\nPress Ctrl+C again within 10 seconds to confirm exit.")
        exit_confirmed = True
        def reset_flag():
            global exit_confirmed
            exit_confirmed = False
        threading.Timer(10.0, reset_flag).start()

async def main():
    global permissions, chat_history_path, subscription_data, mode_config, chat_mode, llm, model_name, should_exit

    console = Console()
    signal.signal(signal.SIGINT, graceful_exit)

    # Start keyboard listener for ESC key
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print_banner()
    ensure_log_folder()
    chat_history_path = get_today_log_path()
    subscription_data = load_subscription()

    if not is_subscription_active():
        enforce_subscription()

    activate_trial()

    os.makedirs("config", exist_ok=True)
    save_mode("power")
    load_mode()
    mode_config = get_mode_config()

    permissions = load_permissions()

    threading.Thread(target=listen_for_shortcuts, daemon=True).start()

    console.print("Rexode is ready!", style="bold green")

    try:
        llm, model_name = get_llm()
    except (KeyboardInterrupt, EOFError):
        graceful_exit(None, None)
        return

    if model_name == "local_tools":
        console.print("Entering local tools mode...", style="bold green")
        
        while True:
            try:
                user_input = console.input("Local Tool> ").strip()
                if user_input.lower() in ["exit", "quit", "bye"]:
                    console.print("Exiting local tools mode.", style="bold red")
                    break

                parts = user_input.split()
                if not parts:
                    continue

                tool_name = parts[0]
                tool_args = " ".join(parts[1:])

                if tool_name in tools:
                    func, desc = tools[tool_name]
                    try:
                        if tool_name == "HeadlessSearch":
                            result = await func(tool_args)
                            if isinstance(result, list):
                                for i, res in enumerate(result):
                                    console.print(Panel(
                                        f"[bold cyan]Title:[/bold cyan] {res.get('title', 'No Title')}\n"
                                        f"[bold cyan]Link:[/bold cyan] {res.get('link', 'No Link')}\n\n"
                                        f"[bold yellow]Content:[/bold yellow]\n{res.get('content', 'No Content')}",
                                        title=f"Result {i+1}",
                                        border_style="green"
                                    ))
                            else:
                                console.print(Panel(str(result), title=tool_name, border_style="blue"))
                        elif tool_name == "BuildNewTool":
                            result = func(tool_args, llm)
                            console.print(Panel(str(result), title=tool_name, border_style="blue"))
                        elif tool_name == "AnalyzeCode":
                            result = func(tool_args, llm)
                            console.print(Panel(str(result), title=tool_name, border_style="blue"))
                        elif tool_args:
                            result = func(tool_args)
                            console.print(Panel(str(result), title=tool_name, border_style="blue"))
                        else:
                            result = func()
                            console.print(Panel(str(result), title=tool_name, border_style="blue"))
                    except Exception as e:
                        console.print(f"Error executing tool '{tool_name}': {e}", style="bold red")
                else:
                    console.print(f"Unknown tool: {tool_name}", style="bold red")
                    console.print("Available tools:", style="bold yellow")
                    for name, (_, desc) in tools.items():
                        console.print(f"- {name}: {desc}")

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="output")
    agent_tools = [
        Tool.from_function(name=name, func=func, description=desc)
        for name, (func, desc) in tools.items()
        if name not in ["BuildNewTool", "ExecuteNLCommand", "DeleteDirectory", "GitCommit"]
    ]

    # Special handling for tools that require the LLM instance or confirmation
    agent_tools.append(Tool.from_function(
        name="BuildNewTool",
        func=lambda instruction: tools["BuildNewTool"][0](instruction, llm),
        description=tools["BuildNewTool"][1]
    ))
    agent_tools.append(Tool.from_function(
        name="ExecuteNLCommand",
        func=lambda command: tools["ExecuteNLCommand"][0](command, confirm=True),
        description=tools["ExecuteNLCommand"][1]
    ))
    agent_tools.append(Tool.from_function(
        name="DeleteDirectory",
        func=lambda path: tools["DeleteDirectory"][0](path, confirm=True),
        description=tools["DeleteDirectory"][1]
    ))
    agent_tools.append(Tool.from_function(
        name="AnalyzeCode",
        func=lambda code_input: tools["AnalyzeCode"][0](code_input, llm),
        description=tools["AnalyzeCode"][1]
    ))
    agent_tools.append(Tool.from_function(
        name="GitCommit",
        func=lambda message: tools["GitCommit"][0](message, llm),
        description=tools["GitCommit"][1]
    ))

    # Initialize InlineActivityIndicator for the agent
    agent_indicator = InlineActivityIndicator(console, "Rexode is thinking...")

    agent = initialize_agent(
        agent_tools,
        llm,
        agent= "conversational-react-description",
        verbose=False,
        handle_parsing_errors=True,
        memory=memory,
        agent_kwargs={
            "system_message": "You are Rexode, a helpful AI assistant. You have access to various tools to assist the user. Be proactive and use your tools when necessary. If asked for general knowledge, try to answer directly from your training data before resorting to web search. Always provide clear and concise answers."
        }
    )

    while not should_exit:
        try:
            if chat_mode == "voice":
                user_input = get_voice_input()
                if not user_input:
                    continue
                console.print(Panel(user_input, title="You", title_align="left", border_style="blue"))
            else:
                user_input = console.input(f"You ({model_name})> ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("Goodbye from Rexode.", style="bold red")
                break

            append_chat(f"You: {user_input}", f"")
            
            # Start indicator before invoking the agent
            agent_indicator.start()
            
            response_content = ""
            async def get_response_stream(indicator: InlineActivityIndicator):
                nonlocal response_content
                async for chunk in agent.astream({"input": user_input}):
                    if cancel_event.is_set():
                        raise asyncio.CancelledError
                    if "output" in chunk:
                        response_content += chunk["output"]

            # Create a cancellable task for agent invocation
            agent_task = asyncio.create_task(get_response_stream(agent_indicator)) # Pass indicator here
            
            try:
                await agent_task # Await the task that consumes the stream
            except asyncio.CancelledError:
                response_content = "Task cancelled by user."
            except Exception as e:
                response_content = f"An error occurred: {e}"
            finally:
                # Ensure indicator is stopped and event is cleared
                agent_indicator.stop()
                sys.stdout.write("\r" + " " * console.width + "\r") # Force clear the line
                sys.stdout.flush()
                console.print() # Ensure a fresh line for the panel
                cancel_event.clear() # Clear the event for the next input

            console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))

            # The streamed content is already displayed by the indicator, so no need for a separate panel here.
            # console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))
            console.print(f"[dim]Model: {model_name}[/dim]", justify="right")
            append_chat(f"", f"Rexode: {response_content}")
            time.sleep(2)

        except (KeyboardInterrupt, EOFError):
            graceful_exit(None, None)
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")
            console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))
            console.print(f"[dim]Model: {model_name}[/dim]", justify="right")
            append_chat(f"", f"Rexode: {response_content}")
            time.sleep(2)

        except (KeyboardInterrupt, EOFError):
            graceful_exit(None, None)
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")

if __name__ == "__main__":
    asyncio.run(main())