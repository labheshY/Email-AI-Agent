from email_code import get_full_emails, get_label_ids, add_label, trash_message
from classify_and_reply import classify_email, generate_reply, is_likely_newsletter, is_marketing_sender
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import json
import os
from google.oauth2.credentials import Credentials
from load_save_cache import load_cache, save_cache, limit_cache_size
from memory import load_thread_memory, save_thread_memory
from send_email import send_email
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_emails():
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        service = build('gmail', 'v1', credentials=creds)
        
        thread_memory = load_thread_memory()

        label_map = get_label_ids(service)
        REPLIED_LABEL = label_map.get("AI_REPLIED")
        SKIPPED_LABEL = label_map.get("AI_SKIPPED")
        FAILED_LABEL = label_map.get("AI_FAILED")
        
        emails = get_full_emails()
        
        # Check settings
        AUTO_REPLY = os.environ.get("AUTO_REPLY", "false").lower() == "true"
        AUTO_DELETE_SPAM = os.environ.get("AUTO_DELETE_SPAM", "false").lower() == "true"
        
    except Exception as e:
        logger.error(f"Failed to initialize Gmail service or fetch emails: {e}")
        return

    cache = load_cache()
    for e in emails:
        logger.info("==============================")
        msg_id = e["id"]
        subject = e["subject"]
        body = e["body"]

        logger.info(f"Subject: {subject}")
        
        # Cache check
        if msg_id in cache:
            logger.info("⚡ Loaded from cache")
            logger.info(f"Category: {cache[msg_id]['category']}")
            logger.info("\n------Generated Reply------")
            logger.info(cache[msg_id]["reply"][:300])
            continue

        # Rule based classify
        if is_likely_newsletter(subject, body) or is_marketing_sender(e["from"]):
            logger.info("Newsletter or no-reply detected (rule-based)")
            cache[msg_id] = {
                "category": "NOTIFICATION",
                "reply": "",
                "status": "skipped",
                "timestamp": datetime.now().isoformat()
            }
            add_label(service, msg_id, SKIPPED_LABEL)
            save_cache(cache)
            continue
        
        # AI Classify
        try:
            category = classify_email(subject, body)
            logger.info(f"Category: {category}")
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            logger.error("❌ Classification error")

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
        if category == "SPAM":
            if AUTO_DELETE_SPAM:
                logger.info("Moving SPAM email to trash")
                try:
                    trash_message(service, msg_id)
                    cache[msg_id] = {
                        "category": category,
                        "reply": "",
                        "status": "trashed",
                        "timestamp": datetime.now().isoformat()
                    }
                    save_cache(cache)
                except Exception as e:
                    logger.error(f"Failed to trash message: {e}")
            else:
                logger.info("Skipping SPAM email (Auto-delete disabled)")
                cache[msg_id] = {
                    "category": category,
                    "reply": "",
                    "status": "skipped",
                    "timestamp": datetime.now().isoformat()
                }
                add_label(service, msg_id, SKIPPED_LABEL)
                save_cache(cache)
            continue

        if category in ["SALES", "NOTIFICATION"]:
            cache[msg_id] = {
                "category": category,
                "reply": "",
                "status": "skipped",
                "timestamp": datetime.now().isoformat()
            }
            add_label(service, msg_id, SKIPPED_LABEL)
            save_cache(cache)
            continue


        if category == "PERSONAL" or category == "SUPPORT":
            thread_id = e["thread_id"]

            thread_context = thread_memory.get(thread_id, [])

            context_text = ""
            if thread_context:
                context_text = "Previous conversation:\n"
                for msg in thread_context:
                    context_text += f"- {msg['subject']}: {msg['body']}\n"
            try:
                reply = generate_reply(subject, body, category, e.get("name"), context_text)
            except Exception as e:
                logger.error(f"Gemini error: {e}")
                logger.error("❌ Reply error")

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
            logger.info("\n------Generated Reply------")
            logger.info(reply[:300])
            logger.info(f"Sending email to: {to_email}")
            
            if not AUTO_REPLY:
                confirm = input("Send? (y/n): ")
                if confirm.lower() != "y":
                    logger.info("Skipped by user")
    
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
            if thread_id not in thread_memory:
                thread_memory[thread_id] = []

            thread_memory[thread_id].append({
                "subject": subject,
                "body": body[:200]
            })

            # keep only last 2 messages
            thread_memory[thread_id] = thread_memory[thread_id][-2:]

            save_thread_memory(thread_memory)
            logger.info("Email Sent")
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
    
    # Try sending daily summary
    send_daily_summary(service, cache)

def send_daily_summary(service, cache):
    state_file = "summary_state.json"
    now = datetime.now()
    
    last_sent = None
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            data = json.load(f)
            if "last_sent" in data:
                last_sent = datetime.fromisoformat(data["last_sent"])
                
    # Target time to send summary (24-hour format, default 18 = 6 PM)
    TARGET_HOUR = int(os.environ.get("SUMMARY_TIME_HOUR", "18"))
    
    # Check if we are in the target hour
    if now.hour != TARGET_HOUR:
        return
        
    # Check if we've already sent it today
    if last_sent and last_sent.date() == now.date():
        return 
        
    logger.info("Generating and sending Daily Summary...")
    one_day_ago = now - timedelta(days=1)
    
    replied_count = 0
    skipped_count = 0
    spam_count = 0
    failed_count = 0
    
    summary_details = ""
    
    for msg_id, data in cache.items():
        if "timestamp" in data:
            try:
                msg_time = datetime.fromisoformat(data["timestamp"])
                if msg_time > one_day_ago:
                    status = data.get("status", "")
                    category = data.get("category", "")
                    
                    if status == "replied":
                        replied_count += 1
                        summary_details += f"- {data.get('subject', 'No subject')} ({category}) from {data.get('sender', 'Unknown')}\n"
                    elif status == "trashed" or category == "SPAM":
                        spam_count += 1
                    elif "skipped" in status:
                        skipped_count += 1
                    elif "failed" in status:
                        failed_count += 1
            except ValueError:
                continue
                
    body = f"""
Hi Labhesh,

Here’s your AI Email Agent summary for the last 24 hours:

📊 Overview:
- Total processed: {replied_count + skipped_count + spam_count + failed_count}
- Replied: {replied_count}
- Skipped (newsletters/sales): {skipped_count}
- Spam/Trashed: {spam_count}
- Failed: {failed_count}

📌 Important interactions:
{summary_details if summary_details else "- No important emails handled"}

⚠️ Attention needed:
{"- Some emails failed to process" if failed_count > 0 else "- No issues detected"}

Let me know if you'd like a more detailed breakdown.

Best regards,  
Your AI Assistant
"""
    
    try:
        profile = service.users().getProfile(userId='me').execute()
        user_email = profile['emailAddress']
        
        send_email(service, user_email, "Daily AI Agent Summary", body, None, None)
        logger.info("Daily summary sent successfully!")
        
        with open(state_file, "w") as f:
            json.dump({"last_sent": now.isoformat()}, f)
    except Exception as e:
        logger.error(f"Failed to send daily summary: {e}")

if __name__ == "__main__":
    # Uncomment the below code to run it indefinitely and comment/ remove below call to process_emails()
    # while True:
    #     logger.info("🚀 Checking emails...")
    #     process_emails()

    #     logger.info("⏳ Sleeping for 60 seconds...\n")
    #     time.sleep(60)  # run every 1 min
    process_emails()
