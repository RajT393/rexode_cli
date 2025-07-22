import os
import json
import getpass
from main import get_machine_id
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from datetime import timedelta

LICENSE_FILE = os.path.expanduser("~/.rexode/license.json")

# Initialize Firebase
credential_path = os.path.join(os.path.dirname(__file__), '..', 'firebase_credentials.json')
cred = credentials.Certificate(credential_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_license_key():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            license_data = json.load(f)
            return license_data.get("activation_key")
    return None

def activate_license():
    if get_license_key():
        print("License key already found.")
        return True

    print("Please enter your activation key:")
    activation_key = getpass.getpass()

    licenses_ref = db.collection('licenses')
    query = licenses_ref.where('activation_key', '==', activation_key).limit(1)
    results = query.stream()

    license_doc = None
    for doc in results:
        license_doc = doc

    if not license_doc:
        print("Invalid activation key.")
        return False

    license_data = license_doc.to_dict()

    if license_data.get('activated'):
        print("This key has already been used.")
        return False

    # Get plan details from Firestore (assuming plans are stored there or fetched)
    # For now, we'll rely on the plan name from the license doc
    plan_name = license_data.get('plan') # Use 'plan' field from license doc

    current_time = datetime.datetime.now(datetime.timezone.utc)
    expires_at = None

    if plan_name == "FreeTrial":
        # Assuming trial_duration_days is defined in the plans.json or fetched
        # For now, hardcode 60 days for FreeTrial activation
        trial_duration_days = 60 
        expires_at = current_time + timedelta(days=trial_duration_days)

    machine_id = get_machine_id()
    update_data = {
        'activated': True,
        'machine_id': machine_id,
        'activated_at': firestore.SERVER_TIMESTAMP,
    }
    if expires_at:
        update_data['expires_at'] = expires_at

    license_doc.reference.update(update_data)

    local_license_data = {
        "activation_key": activation_key,
        "machine_id": machine_id,
        "plan": plan_name,
    }
    if expires_at:
        local_license_data['expires_at'] = expires_at.isoformat() # Store as ISO format string

    os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
    with open(LICENSE_FILE, 'w') as f:
        json.dump(local_license_data, f)

    print(f"Activation successful! You are on the {plan_name} plan.")
    if expires_at:
        print(f"Your plan expires on {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}.")
    return True

if __name__ == '__main__':
    activate_license()
