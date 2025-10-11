import re
import logging
import random
from langdetect import detect, LangDetectException
from googletrans import Translator
from insights import models as insight_models
from emoji import demojize, EMOJI_DATA  # For emoji detection
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)
translator = Translator()

# =========================
# 📌 NLP Analysis Functions
# =========================
def analyze_text(text: str, method="ml") -> dict:
    """
    Analyze text sentiment using ML sentiment model or fallback.
    Handles emoji-only posts, very short posts, and non-English text.
    Returns {original, translated, label}.
    """
    if not text or text.strip() == "":
        return {"original": text, "translated": text, "label": "neutral"}

    original_text = text.strip()

    # Emoji-only check
    if all(char in EMOJI_DATA or char.isspace() for char in original_text):
        logger.debug(f"Emoji-only post detected: {original_text}")
        return {"original": original_text, "translated": original_text, "label": "neutral"}

    # Convert emojis to text
    processed_text = demojize(original_text)

    # Skip very short posts (<4 characters after conversion)
    if len(processed_text) < 4:
        logger.debug(f"Short post skipped for sentiment: {processed_text}")
        return {"original": original_text, "translated": processed_text, "label": "neutral"}

    translated_text = processed_text

    # Detect language & translate
    try:
        lang = detect(processed_text)
    except LangDetectException:
        lang = "en"

    if lang != "en":
        try:
            translated_text = translator.translate(processed_text, dest="en").text
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            translated_text = processed_text

    label = "neutral"

    # ML Sentiment Prediction
    if method == "ml" and insight_models.sentiment_model:
        try:
            pred = insight_models.sentiment_model.predict([translated_text])
            logger.debug(f"Original: {original_text}, Translated: {translated_text}, Raw Prediction: {pred}")

            pred_value = pred[0]
            if isinstance(pred_value, str):
                label = pred_value.lower()
            elif isinstance(pred_value, int):
                label = {0: "negative", 1: "neutral", 2: "positive"}.get(pred_value, "neutral")
            else:
                label = "neutral"
        except Exception as e:
            logger.error(f"Sentiment model error: {e}")
            label = "neutral"
    else:
        logger.info("ML method not used or sentiment model not loaded.")

    return {"original": original_text, "translated": translated_text, "label": label}


# =========================
# 📌 Extra Analysis Features
# =========================

def mentions_location(text: str):
    """
    Check if text contains a city/country from locations_model dataset.
    Returns matched location (city/country) or None.
    """
    if not text:
        return None

    lowered = text.lower()

    # 1. Check in dataset
    if insight_models.locations_model:
        try:
            for entry in insight_models.locations_model:
                if isinstance(entry, (list, tuple)) and len(entry) >= 3:
                    city, country = entry[1].lower(), entry[2].lower()
                    if city in lowered:
                        return entry[1]
                    if country in lowered:
                        return entry[2]
                elif isinstance(entry, dict):
                    city = entry.get("city", "").lower()
                    country = entry.get("country", "").lower()
                    if city and city in lowered:
                        return entry["city"]
                    if country and country in lowered:
                        return entry["country"]
        except Exception as e:
            logger.error(f"Location model error: {e}")

    # 2. Fallback: manually check common Sri Lankan cities
    fallback_cities = [
        "colombo", "kandy", "galle", "jaffna", "batticaloa",
        "trincomalee", "negombo", "kurunegala", "anuradhapura",
        "ratnapura", "badulla", "matara"
    ]
    for city in fallback_cities:
        if city in lowered:
            return city.capitalize()

    return None



def is_toxic(text: str) -> bool:
    """
    Uses the toxic_model + keyword fallback.
    Returns True if text is toxic.
    """
    if not text:
        return False

    # keyword fallback
    toxic_keywords = ["shit", "fuck", "bitch", "asshole", "bastard"]
    lowered = text.lower()
    keyword_match = any(word in lowered for word in toxic_keywords)

    # model check
    model_prediction = False
    if insight_models.toxic_model:
        try:
            model_prediction = bool(insight_models.toxic_model.predict([text])[0])
        except Exception as e:
            logger.error(f"Toxic model error: {e}")

    return model_prediction or keyword_match


def is_respectful(text: str) -> bool:
    """
    Respectful = not toxic.
    """
    return not is_toxic(text)


def discloses_personal_info(text: str) -> bool:
    if not text:
        return False
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"
    return bool(re.search(email_pattern, text) or re.search(phone_pattern, text))


def is_potential_misinformation(text: str) -> bool:
    if not text or not insight_models.misinfo_model:
        return False
    try:
        return bool(insight_models.misinfo_model.predict([text])[0])
    except Exception as e:
        logger.error(f"Misinfo model error: {e}")
        return False


# =========================
# 📌 Metrics & Random Recommendations
# =========================
def compute_insight_metrics(insights: list):
    total = len(insights) or 1
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    night_posts = 0
    location_mentions = 0
    respectful_count = 0

    # Set your local timezone (Sri Lanka example)
    local_tz = pytz.timezone("Asia/Colombo")

    for item in insights:
        # ✅ Count sentiment
        label = (item.get("label") or "").lower()
        if label in sentiment_counts:
            sentiment_counts[label] += 1

        # ✅ Handle timestamp properly
        if item.get("timestamp"):
            try:
                dt = datetime.fromisoformat(item["timestamp"].replace("Z", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                dt_local = dt.astimezone(local_tz)
                hour = dt_local.hour

                # Night post = 11pm → 6am
                if hour >= 23 or hour < 6:
                    night_posts += 1
            except Exception as e:
                logger.warning(f"Invalid timestamp format: {item['timestamp']} ({e})")

        # ✅ Location mentions
        if item.get("mentions_location"):
            location_mentions += 1

        # ✅ Respectful check
        if item.get("is_respectful"):
            respectful_count += 1
        
        if item.get("is_potential_misinformation"):
            respectful_count -= 1 
    # Metrics
    insightMetrics = [
        {"title": "Happy Posts", "value": round((sentiment_counts['positive'] / total) * 100)},
        {"title": "Good Posting Habits", "value": round(100 - (night_posts / total) * 100)},
        {"title": "Privacy Care", "value": round(100 - (location_mentions / total) * 100)},
        {"title": "Being Respectful", "value": round((respectful_count / total) * 100)},
    ]

    # Recommendation logic
    pos_percent = (sentiment_counts['positive'] / total) * 100
    healthy_percent = 100 - (night_posts / total) * 100
    privacy_percent = 100 - (location_mentions / total) * 100
    respect_percent = (respectful_count / total) * 100

    rec_pool = {
        "positive": ["Your interactions are highly positive.", "Keep spreading positivity!", "Great positive engagement!"],
        "positive_medium": ["Some interactions could be more positive.", "Try to keep posts positive.", "Consider uplifting content."],
        "positive_low": ["Work on improving positivity in your posts.", "Posts could use a more positive tone."],
        "healthy": ["Healthy posting schedule.", "Good activity balance.", "Great job avoiding late-night posts."],
        "unhealthy": ["Reduce late-night activity.", "Avoid posting during sleep hours.", "Late-night posts could affect health."],
        "privacy_good": ["Minimal location info shared.", "Good privacy habits.", "Careful with location sharing."],
        "privacy_bad": ["Location sharing is frequent, adjust settings.", "Be mindful of locations you post."],
        "respect_high": ["Excellent respect in interactions.", "Communicate respectfully.", "Keep polite tone."],
        "respect_medium": ["Some comments may be disrespectful.", "Improve respectful interactions.", "Tone could be more polite."],
        "respect_low": ["Improve tone and respectfulness.", "Avoid disrespectful language.", "Work on respectful communication."]
    }

    recommendations = []
    if pos_percent >= 80:
        recommendations.append({"text": random.choice(rec_pool["positive"])})
    elif pos_percent >= 50:
        recommendations.append({"text": random.choice(rec_pool["positive_medium"])})
    else:
        recommendations.append({"text": random.choice(rec_pool["positive_low"])})

    recommendations.append({"text": random.choice(rec_pool["healthy"] if healthy_percent >= 80 else rec_pool["unhealthy"])})
    recommendations.append({"text": random.choice(rec_pool["privacy_good"] if privacy_percent >= 80 else rec_pool["privacy_bad"])})
    
    if respect_percent >= 75:
        recommendations.append({"text": random.choice(rec_pool["respect_high"])})
    elif respect_percent >= 50:
        recommendations.append({"text": random.choice(rec_pool["respect_medium"])})
    else:
        recommendations.append({"text": random.choice(rec_pool["respect_low"])})

    return insightMetrics, recommendations
