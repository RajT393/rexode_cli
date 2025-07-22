# permissions.py

import json
import os

PERMISSIONS_FILE = "permissions.json"

def load_permissions():
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_permissions(perms):
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(perms, f, indent=2)

def ask_permission(task_name: str) -> str:
    perms = load_permissions()
    if task_name in perms:
        return perms[task_name]

    print(f"\n⚠️ Permission Required for: {task_name}")
    print("1. Allow Once")
    print("2. Always Allow")
    print("3. Edit Externally")
    print("4. ESC / Cancel")

    choice = input("Choose [1-4]: ").strip()
    if choice == "1":
        return "once"
    elif choice == "2":
        perms[task_name] = "always"
        save_permissions(perms)
        return "always"
    elif choice == "3":
        return "external"
    else:
        return "deny"
