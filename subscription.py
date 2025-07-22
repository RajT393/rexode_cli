import json
import os
from datetime import datetime, timedelta

SUBSCRIPTION_FILE = "subscription.json"

def load_subscription():
    if not os.path.exists(SUBSCRIPTION_FILE):
        return {"plan": "free", "expires": None}
    
    with open(SUBSCRIPTION_FILE, "r") as f:
        return json.load(f)

def is_subscription_active():
    sub = load_subscription()
    if sub["plan"] == "free":
        return True
    if sub["expires"]:
        try:
            expiry = datetime.strptime(sub["expires"], "%Y-%m-%d")
            return datetime.now() <= expiry
        except:
            return False
    return False

def enforce_subscription():
    if not is_subscription_active():
        print("🔒 Your subscription has expired. Please subscribe at https://rexode.in to continue using premium features.")
        exit(0)

def activate_trial(days=30):
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    sub = {"plan": "trial", "expires": expiry}
    with open(SUBSCRIPTION_FILE, "w") as f:
        json.dump(sub, f, indent=2)
    print(f"Trial activated! Expires on {expiry}")
