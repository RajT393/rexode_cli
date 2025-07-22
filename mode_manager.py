import json

MODE_FILE = "config/mode_config.json"

MODES = {
    "power": {"speed": "fast", "accuracy": "high"},
    "balanced": {"speed": "medium", "accuracy": "medium"},
    "eco": {"speed": "slow", "accuracy": "low"}
}

def load_mode():
    try:
        with open(MODE_FILE, "r") as f:
            data = json.load(f)
        return data.get("mode", "balanced")
    except:
        return "balanced"

def save_mode(mode):
    with open(MODE_FILE, "w") as f:
        json.dump({"mode": mode}, f)

def get_mode_config():
    return MODES.get(load_mode(), MODES["balanced"])

# Switch mode (e.g. from shortcut Ctrl+Alt+M)
def switch_mode():
    current = load_mode()
    modes = list(MODES.keys())
    idx = (modes.index(current) + 1) % len(modes)
    new_mode = modes[idx]
    save_mode(new_mode)
    return new_mode
