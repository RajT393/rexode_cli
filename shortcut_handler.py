import keyboard
import threading
import time
from utils import switch_mode, notify_user
from ocr_reader import capture_and_ocr

def listen_for_shortcuts():
    def monitor():
        last_m_pressed = False
        last_s_pressed = False
        while True:
            m_now = keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed('m')
            s_now = keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed('s')

            if m_now and not last_m_pressed:
                mode = "power"  # Set to default or toggle
                result = switch_mode(mode)
                notify_user(result)
                last_m_pressed = True
            elif not m_now:
                last_m_pressed = False

            if s_now and not last_s_pressed:
                text = capture_and_ocr()
                notify_user("📸 Screen OCR Text:\n" + text)
                last_s_pressed = True
            elif not s_now:
                last_s_pressed = False

            time.sleep(0.2)  # Prevent CPU overload

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
