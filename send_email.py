import base64
from email.mime.text import MIMEText

def send_email(service, to, subject, reply_text, thread_id, message_id):
    message = MIMEText(reply_text)
    message["to"] = to
    if not subject.lower().startswith("re:"):
        message["subject"] = "Re: " + subject

    if message_id:
        message['In-Reply-To'] = message_id
        message['References'] = message_id

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    message_body = {
        'raw': raw_message,
        'threadId': thread_id
    }

    service.users().messages().send(userId="me", body=message_body).execute()