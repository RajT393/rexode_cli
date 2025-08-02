import threading
import time
import datetime
import platform
import os
import pyautogui
import pyttsx3
import pywhatkit

# ========== Notification ==========
def notify(title, message):
    try:
        from notifypy import Notify
        notification = Notify()
        notification.title = title
        notification.message = message
        notification.send()
    except ImportError:
        print(f"🔔 {title}: {message}")
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.MessageBeep()
            else:
                os.system("say 'Notification'")
        except:
            pass

# ========== Text-to-Speech ==========
speak = pyttsx3.init()
def say(msg):
    speak.say(msg)
    speak.runAndWait()

# ========== Task Storage ==========
pending_tasks = []

# ========== Time Parsing ==========
def parse_time_input(input_str):
    parts = input_str.split("|||")
    if len(parts) == 2:
        return parts[0], parts[1]  # task, time
    elif len(parts) == 3:
        return parts[0], parts[1], parts[2]  # phone, msg, time
    return parts

def seconds_until(time_str):
    target = datetime.datetime.strptime(time_str, "%H:%M").time()
    now = datetime.datetime.now().time()
    today = datetime.date.today()

    target_dt = datetime.datetime.combine(today, target)
    now_dt = datetime.datetime.combine(today, now)
    if target_dt < now_dt:
        target_dt += datetime.timedelta(days=1)

    return (target_dt - now_dt).seconds

# ========== Reminders ==========
def remind_task(input_str):
    task, time_str = parse_time_input(input_str)
    sec = seconds_until(time_str)
    pending_tasks.append(("reminder", task, time_str))

    say(f"Reminder set for {time_str}: {task}")
    notify("Reminder Set", f"Will alert at {time_str}: {task}")

    def task_fn():
        time.sleep(sec)
        notify("⏰ Reminder", task)
        say(f"Reminder: {task}")

    threading.Thread(target=task_fn, daemon=True).start()
    return f"⏰ Reminder set for {time_str}"

# ========== WhatsApp Messages ==========
def schedule_whatsapp_msg(phone, message, time_str):
    hour, minute = map(int, time_str.strip().split(":"))
    pending_tasks.append(("whatsapp", f"To {phone}: {message}", time_str))
    
    say(f"WhatsApp message scheduled for {time_str}")
    notify("📨 WhatsApp Scheduled", f"To: {phone}, At: {time_str}")

    def send():
        pywhatkit.sendwhatmsg(phone, message, hour, minute, wait_time=10)

    threading.Thread(target=send, daemon=True).start()
    return f"📨 WhatsApp will be sent to {phone} at {time_str}"

# ========== YouTube Controls ==========
def pause_video_later(seconds):
    say(f"Pausing video in {seconds} seconds")
    notify("⏸️ Video", f"Will pause in {seconds} seconds")

    def pause():
        time.sleep(seconds)
        pyautogui.press("k")
        say("Video paused.")

    threading.Thread(target=pause, daemon=True).start()
    return f"⏸️ Video will pause after {seconds} seconds."

def next_video_later(seconds):
    say(f"Next video will play in {seconds} seconds")
    notify("⏭️ Video", f"Will skip in {seconds} seconds")

    def next_vid():
        time.sleep(seconds)
        pyautogui.press("shift")
        pyautogui.press("n")
        say("Next video played.")

    threading.Thread(target=next_vid, daemon=True).start()
    return f"⏭️ Will skip to next video after {seconds} seconds."

# ========== Task Listing ==========
def list_pending_tasks():
    if not pending_tasks:
        return "✅ No pending scheduled tasks."
    return "\n".join([
        f"{i+1}. {task_type.upper()} at {time} -> {task}"
        for i, (task_type, task, time) in enumerate(pending_tasks)
    ])
