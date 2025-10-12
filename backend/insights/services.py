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
def remove_variation_selectors(text: str) -> str:
    """Remove variation selectors (U+FE0F) to normalize emojis."""
    return text.replace("\ufe0f", "")

def analyze_text(text: str, method="ml") -> dict:
    if not text or text.strip() == "":
        return {"original": text, "translated": text, "label": "neutral"}

    original_text = text.strip()
    clean_text = remove_variation_selectors(original_text)

    # ---------- Emoji-only check ----------
    if all(char in EMOJI_DATA or char.isspace() for char in clean_text):
        positive_emojis = {"❤️", "❤", "💖", "😍", "😂", "😊", "🥰", "👍"}
        negative_emojis = {"😢", "😡", "💔", "😠", "😞"}

        if any(remove_variation_selectors(e) in clean_text for e in positive_emojis):
            return {"original": original_text, "translated": original_text, "label": "positive"}
        if any(remove_variation_selectors(e) in clean_text for e in negative_emojis):
            return {"original": original_text, "translated": original_text, "label": "negative"}
        return {"original": original_text, "translated": original_text, "label": "neutral"}

    # ---------- Emoji-heavy posts (>50%) ----------
    emoji_ratio = sum(1 for ch in clean_text if ch in EMOJI_DATA) / len(clean_text)
    if emoji_ratio > 0.5:
        return {"original": original_text, "translated": original_text, "label": "positive"}

    # ---------- Convert emojis to text for ML ----------
    processed_text = demojize(original_text)
    if len(processed_text) < 4:
        return {"original": original_text, "translated": processed_text, "label": "neutral"}

    translated_text = processed_text

    # ---------- Language detection & translation ----------
    try:
        lang = detect(processed_text)
    except LangDetectException:
        lang = "en"

    if lang != "en":
        try:
            translated_text = translator.translate(processed_text, dest="en").text
        except Exception:
            translated_text = processed_text

    # ---------- ML Sentiment Prediction ----------
    label = "neutral"
    if method == "ml":
        sentiment_model = insight_models.get_sentiment_model()
        if sentiment_model:
            try:
                pred = sentiment_model.predict([translated_text])
                pred_value = pred[0]
                if isinstance(pred_value, str):
                    label = pred_value.lower()
                elif isinstance(pred_value, int):
                    label = {0: "negative", 1: "neutral", 2: "positive"}.get(pred_value, "neutral")
            except Exception as e:
                logger.error(f"Sentiment model error: {e}")

    return {"original": original_text, "translated": translated_text, "label": label}


# =========================
# 📌 Extra Analysis Features
# =========================
def mentions_location(text: str):
    if not text:
        return None

    lowered = text.lower()
    locations_model = insight_models.get_locations_model()
    if locations_model:
        try:
            for entry in locations_model:
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
    if not text:
        return False

    toxic_keywords = ["shit", "fuck", "bitch", "asshole", "bastard"]
    lowered = text.lower()
    keyword_match = any(word in lowered for word in toxic_keywords)

    model_prediction = False
    toxic_model = insight_models.get_toxic_model()
    if toxic_model:
        try:
            model_prediction = bool(toxic_model.predict([text])[0])
        except Exception as e:
            logger.error(f"Toxic model error: {e}")

    return model_prediction or keyword_match


def is_respectful(text: str) -> bool:
    return not is_toxic(text)


def discloses_personal_info(text: str) -> bool:
    if not text:
        return False
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"
    return bool(re.search(email_pattern, text) or re.search(phone_pattern, text))


def is_potential_misinformation(text: str) -> bool:
    if not text or text.strip() == "":
        return False

    non_emoji_chars = sum(1 for ch in text if ch not in EMOJI_DATA and not ch.isspace())
    if non_emoji_chars < 4:
        return False

    misinfo_model = insight_models.get_misinfo_model()
    if not misinfo_model:
        return False

    try:
        pred = misinfo_model.predict([text])[0]
        if isinstance(pred, (int, float)):
            return bool(round(pred))
        if isinstance(pred, str):
            return pred.lower() in ["true", "yes", "1", "misinfo", "misinformation"]
        if isinstance(pred, (list, tuple)):
            return pred[0] > 0.5
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

    local_tz = pytz.timezone("Asia/Colombo")

    for item in insights:
        label = (item.get("label") or "").lower()
        if label in sentiment_counts:
            sentiment_counts[label] += 1

        if item.get("timestamp"):
            try:
                dt = datetime.fromisoformat(item["timestamp"].replace("Z", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                dt_local = dt.astimezone(local_tz)
                hour = dt_local.hour
                if hour >= 23 or hour < 6:
                    night_posts += 1
            except Exception as e:
                logger.warning(f"Invalid timestamp format: {item['timestamp']} ({e})")

        if item.get("mentions_location"):
            location_mentions += 1

        if item.get("is_respectful"):
            respectful_count += 1

    insightMetrics = [
        {"title": "Happy Posts", "value": round((sentiment_counts['positive'] / total) * 100)},
        {"title": "Good Posting Habits", "value": round(100 - (night_posts / total) * 100)},
        {"title": "Privacy Care", "value": round(100 - (location_mentions / total) * 100)},
        {"title": "Being Respectful", "value": round((respectful_count / total) * 100)},
    ]

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
