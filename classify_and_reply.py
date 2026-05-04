from email_code import get_full_emails
from google import genai

client = genai.Client()


def classify_email(subject, body):
    prompt = f"""
        You are an email classification system.

        Categories:
        - SUPPORT → user explicitly asking for help, issue, or question
        - PERSONAL → casual or conversational message without request
        - SALES → promotions, offers, marketing
        - SPAM → irrelevant/junk
        - URGENT → security, money, deadlines

        Return ONLY one word.

        Email:
        Subject: {subject}
        Body: {body}
        """
    
    response = client.models.generate_content(
            model = "gemini-2.5-flash-lite",
            contents=prompt
        )
    
    return response.text.strip()

def generate_reply(subject, body, category, name=None):

    greeting = f"Hi {name}," if name else "Hi,"
    
    prompt = f"""
        You are an AI email assistant.

        Your job:
        Write a REAL email reply.

        Start with this greeting:
        {greeting}

        STRICT RULES:
        - Do NOT ask for more information
        - Do NOT give multiple options
        - Do NOT include placeholders like {{name}} or {{subject}}
        - Do NOT explain anything
        - ONLY output the final email reply

        STYLE:
        - Professional
        - Concise
        - Human-like

        CONTEXT:
        Category: {category}
        Subject: {subject}
        Email Body: {body}

        Now write the reply.
        """

    response = client.models.generate_content( 
            model = "gemini-2.5-flash-lite",
            contents=prompt)

    return response.text.strip()


def is_likely_newsletter(subject, body):
    keywords = ["unsubscribe", "sale", "offer", "discount", "newsletter"]
    text = (subject + body).lower()

    score = sum(word in text for word in keywords)

    return score >= 2   # threshold instead of 1


def is_marketing_sender(sender):
    return any(x in sender.lower() for x in [
        "noreply", "newsletter", "updates", "marketing"
    ])