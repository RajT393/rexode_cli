import os
import json
import datetime
import platform

def split_input(text: str, sep: str = "|||"):
    return [s.strip() for s in text.split(sep)]

def log_chat(user, ai):
    folder = "chat_history"
    os.makedirs(folder, exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(folder, f"{now}.json")
    chat = {"time": str(datetime.datetime.now()), "user": user, "rexode": ai}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []
    history.append(chat)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_mode_config(mode="balanced"):
    return {
        "power": {"features": "All", "speed": "Fast", "limits": "None"},
        "eco": {"features": "Text only", "speed": "Slow", "limits": "Low CPU/RAM"},
        "balanced": {"features": "Most", "speed": "Normal", "limits": "Optimized"},
    }.get(mode, {})

# ✅ ADD this to fix the ImportError
def switch_mode(mode: str):
    os.makedirs(".rexode", exist_ok=True)
    with open(".rexode/mode.json", "w") as f:
        json.dump({"mode": mode}, f)

def notify_user(message: str):
    os_name = platform.system().lower()
    if "windows" in os_name:
        try:
            from win10toast import ToastNotifier
            ToastNotifier().show_toast("Rexode", message, duration=5)
        except:
            print(f"🔔 {message}")
    else:
        # fallback for mac/linux
        print(f"🔔 {message}")
