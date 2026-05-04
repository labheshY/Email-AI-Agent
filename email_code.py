from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parseaddr
import base64

def extract_email(sender):
    name, email = parseaddr(sender)
    return name, email

def get_full_emails():
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)
    query = "in:inbox is:unread newer_than:1d -category:promotions -category:social -label:AI_REPLIED -label:AI_SKIPPED"
    results = service.users().messages().list(userId='me', maxResults=5, q=query).execute()
    messages = results.get('messages', [])

    email_data = []

    for msg in messages:
        msg_detail = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()

        payload = msg_detail['payload']
        headers = payload.get("headers", [])
        thread_id = msg_detail['threadId']
        message_id_header = None
        subject = ""
        sender = ""

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']
            if header['name'] == 'Message-ID':
                message_id_header = header['value']

        body = extract_body(payload)
        name, sender_addr = extract_email(sender)
        cleaned_name = clean_name(name, sender_addr)
        email_data.append({
            "id": msg['id'],
            "thread_id": thread_id,
            "message_id": message_id_header,
            "subject": subject,
            "from": sender,
            "email": sender_addr,
            "name": cleaned_name,
            "body": body
        })

    return email_data

def extract_body(payload):
    body = ""

    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get("mimeType")
            data = part.get("body", {}).get("data")

            if mime_type == "text/plain" and data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")
                return body

    else:
        data = payload.get("body", {}).get("data")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8")

    return body

def clean_name(name, email):
    if name:

        name = name.strip()

        # reject bad names
        bad_keywords = ["noreply", "no-reply", "newsletter", "support", "team"]

        if not any(word in name.lower() for word in bad_keywords) and len(name.split()) <= 3:
            return name

    return extract_name_fallback()


def extract_name_fallback(email):
    username = email.split("@")[0]

    # remove numbers and symbols
    username = username.replace(".", " ").replace("_", " ")

    # capitalize
    name = username.title()

    # avoid bad cases
    if any(x in username for x in ["noreply", "support", "info", "admin"]):
        return None

    return name

def get_label_ids(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    label_map = {label['name']: label['id'] for label in labels}
    return label_map

def add_label(service, msg_id, label_id):
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={
            "addLabelIds": [label_id]
        }
    ).execute()
# emails = get_full_emails()

# for e in emails:
#     print("\n--- EMAIL ---")
#     print("From:", e["from"])
#     print("Subject:", e["subject"])
#     print("Body:", e["body"][:200])  # preview