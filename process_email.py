from email_code import get_full_emails, get_label_ids, add_label
from classify_and_reply import classify_email, generate_reply, is_likely_newsletter, is_marketing_sender
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from load_save_cache import load_cache, save_cache, limit_cache_size
from send_email import send_email


def process_emails():
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)
    
    label_map = get_label_ids(service)
    REPLIED_LABEL = label_map.get("AI_REPLIED")
    SKIPPED_LABEL = label_map.get("AI_SKIPPED")
    FAILED_LABEL = label_map.get("AI_FAILED")
    
    emails = get_full_emails()
    cache = load_cache()
    for e in emails:
        print("\n==============================")
        msg_id = e["id"]
        subject = e["subject"]
        body = e["body"]

        print("Subject:", subject)
        
        # Cache check
        if msg_id in cache:
            print("⚡ Loaded from cache")
            print("Category:", cache[msg_id]["category"])
            print("\n------Generated Reply------")
            print(cache[msg_id]["reply"][:300])
            continue

        # Rule based classify
        if is_likely_newsletter(subject, body) and is_marketing_sender(e["from"]):
            print("Newsletter detected (high confidence)")
            cache[msg_id] = {
                "category": "SALES",
                "reply": "",
                "status": "skipped"
            }
            add_label(service, msg_id, SKIPPED_LABEL)
            save_cache(cache)
            continue
        
        # AI Classify
        try:
            category = classify_email(subject, body)
            print("Category:",category)
        except Exception as e:
            print("Gemini error", e)
            print("❌ Classification error:")

            cache[msg_id] = {
                "category": "ERROR",
                "reply": "",
                "status": "classification_failed",
                "timestamp": datetime.now().isoformat()
            }
            add_label(service, msg_id, FAILED_LABEL)
            save_cache(cache)
            continue

        # Decide Action
        if category in ["SALES", "SPAM"]:
            cache[msg_id] = {
                "category": category,
                "reply": "",
                "status": "skipped"
            }
            add_label(service, msg_id, SKIPPED_LABEL)
            save_cache(cache)
            continue


        if category == "PERSONAL" or category == "SUPPORT":
            try:
                reply = generate_reply(subject, body, category, e.get("name"))
            except Exception as e:
                print("Gemini error", e)
                print("❌ Reply error:", e)

                cache[msg_id] = {
                    "category": category,
                    "reply": "",
                    "status": "reply_failed",
                    "timestamp": datetime.now().isoformat()
                }
                add_label(service, msg_id, FAILED_LABEL)
                save_cache(cache)
                continue
            to_email = e["email"]
            print("\n------Generated Reply------")
            print(reply[:300])
            print(f"Sending email to: {to_email}")
            confirm = input("Send? (y/n): ")

            if confirm.lower() != "y":
                print("Skipped by user")

                cache[msg_id] = {
                    "category": category,
                    "reply": reply,
                    "status": "user_skipped",
                    "timestamp": datetime.now().isoformat()
                }

                save_cache(cache)
                continue
            # send email
            send_email(service, to_email, subject, reply, e["thread_id"], e["message_id"])
            print("Email Sent")
            add_label(service, msg_id, REPLIED_LABEL)
            cache[msg_id]={
                "category": category,
                "reply": reply,
                "subject": subject,
                "sender": e["email"],
                "name": e.get("name"),
                "timestamp": datetime.now().isoformat(),
                "status": "replied"
            }
            save_cache(cache)
    cache = limit_cache_size(cache, max_size=500)
    # save cache
    save_cache(cache)


if __name__ == "__main__":
    process_emails()