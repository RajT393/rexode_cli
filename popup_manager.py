# popup_manager.py

import keyboard

def show_confirmation(task: str) -> str:
    print(f"\n🛑 Task requested: {task}")
    print("➤ Allow once   [→ Enter]")
    print("➤ Allow always [↓ Enter]")
    print("➤ Edit         [↑ Enter]")
    print("➤ Cancel task  [ESC]")
    
    while True:
        if keyboard.is_pressed('esc'):
            print("❌ Task cancelled by user.")
            return "cancel"
        elif keyboard.is_pressed('up'):
            print("✏️  Edit task requested.")
            return "edit"
        elif keyboard.is_pressed('down'):
            print("✅ Always allow this type of task.")
            return "allow_always"
        elif keyboard.is_pressed('enter'):
            print("✅ Task approved once.")
            return "allow_once"
