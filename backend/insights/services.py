# File: services.py
import re
import requests
from langdetect import detect
from textblob import TextBlob
from googletrans import Translator

# Initialize translator once
translator = Translator()

# ✅ Default max posts
DEFAULT_MAX_POSTS = 20
MAX_THREADS = 10


# =========================
# 📌 Facebook Graph Helpers
# =========================
def safe_request(url):
    """Safely fetch JSON from a URL (Facebook Graph)."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print("Request error:", e)
    return {}


def fetch_profile(token):
    """Fetch basic Facebook profile info."""
    url = f"https://graph.facebook.com/me?fields=id,name,birthday,gender,picture.width(150).height(150)&access_token={token}"
    return safe_request(url)


def fetch_comments(post_id, token, limit=5):
    """Fetch top-level comments of a post."""
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments?fields=message,created_time,from,id&limit={limit}&access_token={token}"
    data = safe_request(url)
    return data.get("data", [])


def fetch_nested_comments(comment, token):
    """Fetch replies of a given comment."""
    comment_id = comment.get("id")
    if not comment_id:
        return []
    url = f"https://graph.facebook.com/v19.0/{comment_id}/comments?fields=message,created_time,from,id&limit=5&access_token={token}"
    data = safe_request(url)
    return data.get("data", [])


# =========================
# 📌 NLP Analysis Functions
# =========================
def analyze_text(text, method="nltk"):
    """
    Analyze text sentiment using either NLTK (TextBlob) or ML model.
    Returns {original, translated, label}.
    """
    if not text:
        return {"original": "", "translated": "", "label": "neutral"}

    original_text = text.strip()

    # Detect language & translate if needed
    try:
        lang = detect(original_text)
    except:
        lang = "en"

    translated_text = original_text
    if lang != "en":
        try:
            translated_text = translator.translate(original_text, dest="en").text
        except:
            translated_text = original_text

    label = "neutral"

    if method == "nltk":
        try:
            polarity = TextBlob(translated_text).sentiment.polarity
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
        except:
            label = "neutral"

    elif method == "ml":
        # Placeholder for ML model integration
        try:
            polarity = TextBlob(translated_text).sentiment.polarity
            if polarity > 0.2:
                label = "positive"
            elif polarity < -0.2:
                label = "negative"
        except:
            label = "neutral"

    return {"original": original_text, "translated": translated_text, "label": label}


# =========================
#  Extra Analysis Features
# =========================
def is_respectful(text):
    """Check if text is respectful (very simple keyword-based)."""
    disrespect_words = ["stupid", "idiot", "dumb", "hate", "kill"]
    if not text:
        return True
    lowered = text.lower()
    return not any(word in lowered for word in disrespect_words)


def mentions_location(text):
    """Check if text mentions a location-like word."""
    if not text:
        return False
    patterns = ["colombo", "new york", "paris", "sri lanka", "street", "road", "city"]
    lowered = text.lower()
    return any(word in lowered for word in patterns)


def discloses_personal_info(text):
    """Detect if text discloses personal info (phone/email)."""
    if not text:
        return False
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"
    return bool(re.search(email_pattern, text) or re.search(phone_pattern, text))


def is_toxic(text):
    """Check if text contains toxic words."""
    toxic_words = ["hate", "kill", "trash", "fuck", "bitch", "shit"]
    if not text:
        return False
    lowered = text.lower()
    return any(word in lowered for word in toxic_words)


def is_potential_misinformation(text):
    """Naive misinformation detection (keywords)."""
    if not text:
        return False
    misinfo_patterns = ["flat earth", "fake news", "miracle cure", "hoax", "5g causes covid"]
    lowered = text.lower()
    return any(phrase in lowered for phrase in misinfo_patterns)
