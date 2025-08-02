import pyautogui

def simulate_key_press(key: str) -> str:
    """Simulates a single key press."""
    try:
        pyautogui.press(key)
        return f"✅ Pressed key: {key}"
    except Exception as e:
        return f"❌ Error pressing key '{key}': {e}"

def simulate_type(text: str) -> str:
    """Simulates typing a string of text."""
    try:
        pyautogui.write(text)
        return f"✅ Typed text: {text}"
    except Exception as e:
        return f"❌ Error typing text '{text}': {e}"
