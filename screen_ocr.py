import pytesseract
import pyautogui

def capture_screen_text():
    screenshot = pyautogui.screenshot()
    text = pytesseract.image_to_string(screenshot)
    return text[:2000] if text else "❌ No text detected."
