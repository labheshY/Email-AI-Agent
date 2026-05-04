"""
Adding label to the already cached messages
"""

STATUS_TO_LABEL = {
    "replied": "AI_REPLIED",
    "skipped": "AI_SKIPPED",
    "user_skipped": "AI_SKIPPED",
    "failed": "AI_FAILED",
    "reply_failed": "AI_FAILED",
    "classification_failed": "AI_FAILED",
}

import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from email_code import get_label_ids, add_label  # reuse your helpers

def backfill_labels():
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)

    label_map = get_label_ids(service)

    with open("email_cache.json", "r") as f:
        cache = json.load(f)

    for msg_id, data in cache.items():
        status = data.get("status")
        label_name = STATUS_TO_LABEL.get(status)

        if not label_name:
            continue

        label_id = label_map.get(label_name)
        if not label_id:
            print(f"⚠️ Label missing in Gmail: {label_name}")
            continue

        try:
            add_label(service, msg_id, label_id)
            print(f"✅ Labeled {msg_id} → {label_name}")
        except Exception as e:
            print(f"❌ Failed {msg_id}: {e}")

if __name__ == "__main__":
    backfill_labels()