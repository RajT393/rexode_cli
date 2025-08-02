import pytesseract
import pyautogui

def capture_screen_text():
    screenshot = pyautogui.screenshot()
    try:
        text = pytesseract.image_to_string(screenshot)
        return text[:2000] if text else "❌ No text detected."
    except pytesseract.TesseractNotFoundError:
        return "❌ Tesseract OCR engine not found. Please install Tesseract and ensure it's in your system PATH. Refer to the Rexode documentation for installation instructions."
    except Exception as e:
        return f"❌ An error occurred during OCR: {e}"
