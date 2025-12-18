import re
import logging
import random
from datetime import datetime

import pytz
from langdetect import detect, LangDetectException
from emoji import demojize, EMOJI_DATA

from insights import hf_models as insight_models
from insights.hf_models import map_sentiment_label

logger = logging.getLogger(__name__)

LOCAL_TZ = pytz.timezone("Asia/Colombo")

# =========================
# 🧹 TEXT NORMALIZATION
# =========================
def remove_variation_selectors(text: str) -> str:
    """Remove emoji variation selectors (U+FE0F)."""
    return text.replace("\ufe0f", "")


def is_emoji_only(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and all(
        ch in EMOJI_DATA or ch.isspace() for ch in stripped
    )


# =========================
# 📌 CORE NLP ANALYSIS
# =========================
def analyze_text(text: str, method="ml") -> dict:
    """
    Safe sentiment analysis with:
    - emoji handling
    - lazy translation
    - fail-safe ML execution
    """

    if not text or not text.strip():
        return {
            "original": text,
            "translated": text,
            "label": "neutral",
        }

    original_text = text.strip()
    clean_text = remove_variation_selectors(original_text)

    # -------------------------
    # Emoji-only handling
    # -------------------------
    if is_emoji_only(clean_text):
        positive_emojis = {"😍", "🥰", "❤️", "😂", "😊", "👍"}
        negative_emojis = {"😢", "💔", "😠", "😡", "😞"}

        if any(e in clean_text for e in positive_emojis):
            label = "positive"
        elif any(e in clean_text for e in negative_emojis):
            label = "negative"
        else:
            label = "neutral"

        return {
            "original": original_text,
            "translated": original_text,
            "label": label,
        }

    # -------------------------
    # Emoji → text
    # -------------------------
    processed_text = demojize(clean_text)
    processed_text = processed_text.replace(":", " ").replace("_", " ")

    # -------------------------
    # Language detection
    # -------------------------
    try:
        lang = detect(processed_text)
    except LangDetectException:
        lang = "en"

    translated_text = processed_text

    # -------------------------
    # Lazy translation (safe)
    # -------------------------
    if lang != "en":
        try:
            from googletrans import Translator  # lazy import
            translator = Translator()
            translated_text = translator.translate(
                processed_text, dest="en"
            ).text
        except Exception as e:
            logger.warning(f"[TRANSLATION FAILED] {e}")
            translated_text = processed_text

    # -------------------------
    # Sentiment ML (Updated for API)
    # -------------------------
    label = "neutral"

    if method == "ml":
        sentiment_predictor = insight_models.get_sentiment_model()
        if sentiment_predictor:
            try:
                # The predictor now calls query_hf_api
                pred = sentiment_predictor(translated_text)
                
                # API returns [[{'label': '...', 'score': ...}]]
                if pred and isinstance(pred, list):
                    # Handle nested list or single list response
                    data = pred[0][0] if isinstance(pred[0], list) else pred[0]
                    raw_label = data.get("label", "")
                    score = float(data.get("score", 0))
                    mapped = map_sentiment_label(raw_label)

                    label = mapped if score >= 0.6 else "neutral"
            except Exception as e:
                logger.error(f"[SENTIMENT ERROR] {e}")

    return {
        "original": original_text,
        "translated": translated_text,
        "label": label,
    }


# =========================
# 📍 LOCATION DETECTION
# =========================
def mentions_location(text: str):
    if not text:
        return None

    try:
        entities = insight_models.extract_entities(text)
        locations = entities.get("locations") if entities else None
        if locations:
            return locations[0]
    except Exception as e:
        logger.warning(f"[NER ERROR] {e}")

    fallback_cities = [
        "colombo", "kandy", "galle", "jaffna", "batticaloa",
        "trincomalee", "negombo", "kurunegala", "anuradhapura",
        "ratnapura", "badulla", "matara",
    ]

    lowered = text.lower()
    for city in fallback_cities:
        if city in lowered:
            return city.capitalize()

    return None


# =========================
# ☣️ TOXICITY (Updated for API)
# =========================
def is_toxic(text: str) -> bool:
    if not text:
        return False

    toxic_keywords = {
        "shit", "fuck", "bitch", "asshole", "bastard"
    }

    lowered = text.lower()
    keyword_match = any(word in lowered for word in toxic_keywords)

    toxic_predictor = insight_models.get_toxic_model()
    model_prediction = False

    if toxic_predictor:
        try:
            pred = toxic_predictor(text)
            if pred and isinstance(pred, list):
                # API response handling
                data = pred[0][0] if isinstance(pred[0], list) else pred[0]
                label = str(data.get("label", "")).lower()
                # Check for 'toxic' label or high scores in specific labels
                model_prediction = "toxic" in label or label == "label_1"
        except Exception as e:
            logger.error(f"[TOXIC MODEL ERROR] {e}")

    return keyword_match or model_prediction


def is_respectful(text: str) -> bool:
    return not is_toxic(text)


# =========================
# 🔐 PRIVACY
# =========================
def discloses_personal_info(text: str) -> bool:
    if not text:
        return False

    try:
        entities = insight_models.extract_entities(text)
        return bool(
            entities.get("phones") or entities.get("emails")
        )
    except Exception as e:
        logger.warning(f"[PRIVACY CHECK ERROR] {e}")
        return False


# =========================
# 🧠 MISINFORMATION (Updated for API)
# =========================
def is_potential_misinformation(text: str) -> bool:
    if not text or not text.strip():
        return False

    misinfo_predictor = insight_models.get_misinfo_model()
    if not misinfo_predictor:
        return False

    try:
        pred = misinfo_predictor(text)
        if pred and isinstance(pred, list):
            data = pred[0][0] if isinstance(pred[0], list) else pred[0]
            label = str(data.get("label", "")).lower()
            return label in {"misinfo", "misinformation", "true", "yes", "1", "label_1"}
    except Exception as e:
        logger.error(f"[MISINFO ERROR] {e}")

    return False


# =========================
# 📊 METRICS & RECOMMENDATIONS
# =========================
def compute_insight_metrics(insights: list):
    total = max(len(insights), 1)

    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    night_posts = 0
    location_mentions = 0
    respectful_count = 0

    for item in insights:
        label = (item.get("label") or "").lower()
        if label in sentiment_counts:
            sentiment_counts[label] += 1

        ts = item.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                local_dt = dt.astimezone(LOCAL_TZ)
                if local_dt.hour >= 23 or local_dt.hour < 6:
                    night_posts += 1
            except Exception:
                pass

        if item.get("mentions_location"):
            location_mentions += 1

        if item.get("is_respectful"):
            respectful_count += 1

    insightMetrics = [
        {"title": "Happy Posts", "value": round((sentiment_counts["positive"] / total) * 100)},
        {"title": "Good Posting Habits", "value": round(100 - (night_posts / total) * 100)},
        {"title": "Privacy Care", "value": round(100 - (location_mentions / total) * 100)},
        {"title": "Being Respectful", "value": round((respectful_count / total) * 100)},
    ]

    rec_pool = {
        "positive_high": ["Your interactions are highly positive.", "Keep spreading positivity!"],
        "positive_mid": ["Try sharing more uplifting content.", "Increase positive engagement."],
        "positive_low": ["Focus on improving post positivity."],
        "healthy": ["Great posting schedule.", "Healthy online habits."],
        "unhealthy": ["Reduce late-night posting.", "Late posts can affect wellbeing."],
        "privacy_good": ["Excellent privacy awareness.", "You share minimal sensitive info."],
        "privacy_bad": ["Be cautious when sharing locations."],
        "respect_high": ["Your communication is very respectful."],
        "respect_mid": ["Some posts could be more respectful."],
        "respect_low": ["Avoid harsh language and tone."],
    }

    recommendations = []

    pos_pct = (sentiment_counts["positive"] / total) * 100
    healthy_pct = 100 - (night_posts / total) * 100
    privacy_pct = 100 - (location_mentions / total) * 100
    respect_pct = (respectful_count / total) * 100

    recommendations.append({
        "text": random.choice(
            rec_pool["positive_high"] if pos_pct >= 80 else
            rec_pool["positive_mid"] if pos_pct >= 50 else
            rec_pool["positive_low"]
        )
    })

    recommendations.append({
        "text": random.choice(
            rec_pool["healthy"] if healthy_pct >= 80 else rec_pool["unhealthy"]
        )
    })

    recommendations.append({
        "text": random.choice(
            rec_pool["privacy_good"] if privacy_pct >= 80 else rec_pool["privacy_bad"]
        )
    })

    recommendations.append({
        "text": random.choice(
            rec_pool["respect_high"] if respect_pct >= 75 else
            rec_pool["respect_mid"] if respect_pct >= 50 else
            rec_pool["respect_low"]
        )
    })

    return insightMetrics, recommendations