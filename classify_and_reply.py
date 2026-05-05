from email_code import get_full_emails
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
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
        - NOTIFICATION → automated system emails, newsletters, digests, no-reply

        Return ONLY one word.

        Email:
        Subject: {subject}
        Body: {body}
        """
    
    response = client.models.generate_content(
            model = "gemini-2.5-flash-lite",
            contents=prompt
        )
    
    result = response.text.strip().upper()
    # sometimes it returns ```SUPPORT``` or SUPPORT.
    for cat in ["SUPPORT", "PERSONAL", "SALES", "SPAM", "URGENT", "NOTIFICATION"]:
        if cat in result:
            return cat
    return result

def generate_reply(subject, body, category, name=None, context_text=""):

    greeting = f"Hi {name}," if name else "Hi,"
    
    prompt = f"""
        You are an AI email assistant.

        Your job:
        Write a REAL email reply.

        {context_text}

        STRICT RULES:
        - Write like a busy human engineer. Keep it extremely concise (under 3-4 sentences).
        - Tone should be casual but professional.
        - Directly address the topic without fluff.
        - Do NOT use bullet points or lists unless absolutely necessary.
        - Do NOT use typical AI phrases like "I can definitely help you with that" or "Here are a few common culprits."
        - No placeholders.

        Start with a greeting.
        End with:
        Best regards,
        Labhesh

        Email:
        Subject: {subject}
        Body: {body}
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
        "noreply", "no-reply", "newsletter", "updates", "marketing", 
        "digest", "notification", "system", "quora", "medium"
    ])