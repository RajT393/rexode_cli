# chat_logger.py

import json
import os
from datetime import datetime

CHAT_LOG_FOLDER = "chat_history"

def ensure_log_folder():
    if not os.path.exists(CHAT_LOG_FOLDER):
        os.makedirs(CHAT_LOG_FOLDER)

def get_today_log_path():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(CHAT_LOG_FOLDER, f"rexode_chat_{today}.json")

def append_chat(user_msg: str, ai_msg: str):
    ensure_log_folder()
    log_path = get_today_log_path()
    
    log_data = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []

    log_data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_msg,
        "rexode": ai_msg
    })

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
