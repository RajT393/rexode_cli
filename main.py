import os
import sys
import signal
import threading
import time
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

# Globals
exit_confirmed = False
chat_mode = "text"
permissions = {}
chat_history_path = ""
subscription_data = {}
mode_config = {}
llm = None
model_name = ""

def graceful_exit(sig, frame):
    global exit_confirmed
    if exit_confirmed:
        print("\nExiting Rexode CLI.")
        sys.exit(0)
    else:
        print("\nPress Ctrl+C again within 10 seconds to confirm exit.")
        exit_confirmed = True
        def reset_flag():
            global exit_confirmed
            exit_confirmed = False
        threading.Timer(10.0, reset_flag).start()

def main():
    global permissions, chat_history_path, subscription_data, mode_config, chat_mode, llm, model_name

    console = Console()
    signal.signal(signal.SIGINT, graceful_exit)

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

    console.print("Rexode is ready! Type something or say 'Rexode' to start (in voice mode). Type 'exit' to quit.", style="bold green")

    try:
        llm, model_name = get_llm()
    except (KeyboardInterrupt, EOFError):
        graceful_exit(None, None)
        return

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_tools = [
        Tool.from_function(name=name, func=func, description=desc)
        for name, (func, desc) in tools.items()
    ]

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

    while True:
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
            output = agent.invoke({"input": user_input})
            response_content = output['output']
            console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))
            console.print(f"[dim]Model: {model_name}[/dim]", justify="right")
            append_chat(f"", f"Rexode: {response_content}")
            time.sleep(2)

        except (KeyboardInterrupt, EOFError):
            graceful_exit(None, None)
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")

if __name__ == "__main__":
    main()
