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
    return text.replace("\ufe0f", "")

def is_emoji_only(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and all(ch in EMOJI_DATA or ch.isspace() for ch in stripped)

# =========================
# 📌 CORE NLP ANALYSIS
# =========================
def analyze_text(text: str, method="ml") -> dict:
    if not text or not text.strip():
        return {
            "original": text,
            "translated": text,
            "label": "neutral",
            "confidence": 0.0,
        }

    original_text = text.strip()
    clean_text = remove_variation_selectors(original_text)

    # Emoji-only shortcut
    if is_emoji_only(clean_text):
        positive = {"😍", "🥰", "❤️", "😂", "😊", "👍"}
        negative = {"😢", "💔", "😠", "😡", "😞"}

        if any(e in clean_text for e in positive):
            return {"original": original_text, "translated": original_text, "label": "positive", "confidence": 0.9}
        if any(e in clean_text for e in negative):
            return {"original": original_text, "translated": original_text, "label": "negative", "confidence": 0.9}

        return {"original": original_text, "translated": original_text, "label": "neutral", "confidence": 0.5}

    processed_text = demojize(clean_text).replace(":", " ").replace("_", " ")

    try:
        lang = detect(processed_text)
    except LangDetectException:
        lang = "en"

    translated_text = processed_text
    if lang != "en":
        try:
            from googletrans import Translator
            translated_text = Translator().translate(processed_text, dest="en").text
        except Exception as e:
            logger.warning(f"[TRANSLATION FAILED] {e}")

    label = "neutral"
    confidence = 0.0

    if method == "ml":
        predictor = insight_models.get_sentiment_model()
        if predictor:
            try:
                pred = predictor(translated_text)
                data = pred[0][0] if isinstance(pred[0], list) else pred[0]
                raw_label = data.get("label", "")
                score = float(data.get("score", 0))
                mapped = map_sentiment_label(raw_label)

                label = mapped if score >= 0.6 else "neutral"
                confidence = score
            except Exception as e:
                logger.error(f"[SENTIMENT ERROR] {e}")

    return {
        "original": original_text,
        "translated": translated_text,
        "label": label,
        "confidence": confidence,
    }

# =========================
# 📍 LOCATION DETECTION
# =========================
def mentions_location(text: str):
    if not text:
        return None
    try:
        entities = insight_models.extract_entities(text)
        locs = entities.get("locations")
        return locs[0] if locs else None
    except Exception:
        return None

# =========================
# ☣️ TOXICITY & RESPECT
# =========================
def is_toxic(text: str) -> bool:
    if not text:
        return False

    toxic_keywords = {"shit", "fuck", "bitch", "asshole", "bastard"}
    keyword_match = any(w in text.lower() for w in toxic_keywords)

    predictor = insight_models.get_toxic_model()
    model_pred = False

    if predictor:
        try:
            pred = predictor(text)
            data = pred[0][0] if isinstance(pred[0], list) else pred[0]
            model_pred = "toxic" in str(data.get("label", "")).lower()
        except Exception:
            pass

    return keyword_match or model_pred

def respect_score(item: dict) -> float:
    score = 1.0
    if item.get("toxic", False):
        score -= 0.6
    if item.get("label") == "negative":
        score -= 0.2
    return max(score, 0.0)

def is_respectful(text: str) -> bool:
    return not is_toxic(text)

# =========================
# 🔐 PRIVACY
# =========================
def discloses_personal_info(text: str) -> bool:
    try:
        ent = insight_models.extract_entities(text)
        return bool(ent.get("emails") or ent.get("phones"))
    except Exception:
        return False

def privacy_risk(item: dict) -> float:
    risk = 0.0
    if item.get("mentions_location"):
        risk += 0.4
    if item.get("privacy_disclosure"):
        risk += 0.6
    return min(risk, 1.0)

# =========================
# 🧠 MISINFORMATION
# =========================
def is_potential_misinformation(text: str) -> bool:
    predictor = insight_models.get_misinfo_model()
    if not predictor:
        return False
    try:
        pred = predictor(text)
        data = pred[0][0] if isinstance(pred[0], list) else pred[0]
        return "label_1" in str(data.get("label", "")).lower()
    except Exception:
        return False

# =========================
# 📊 METRICS & RECOMMENDATIONS
# =========================
def compute_insight_metrics(insights: list):
    total = max(len(insights), 1)

    happy_count = 0
    respect_scores = []
    privacy_scores = []

    hour_buckets = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}

    for item in insights:
        if item.get("label") == "positive" and item.get("confidence", 0) >= 0.75:
            happy_count += 1

        respect_scores.append(respect_score(item))
        privacy_scores.append(privacy_risk(item))

        ts = item.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                hour = dt.astimezone(LOCAL_TZ).hour

                if 5 <= hour <= 11:
                    hour_buckets["morning"] += 1
                elif 12 <= hour <= 16:
                    hour_buckets["afternoon"] += 1
                elif 17 <= hour <= 22:
                    hour_buckets["evening"] += 1
                else:
                    hour_buckets["night"] += 1
            except Exception:
                pass

    best_time = max(hour_buckets, key=hour_buckets.get)
    avg_respect = sum(respect_scores) / total
    avg_privacy = sum(privacy_scores) / total

    if avg_privacy < 0.3:
        privacy_profile = "Low Disclosure"
    elif avg_privacy < 0.6:
        privacy_profile = "Moderate Disclosure"
    else:
        privacy_profile = "High Disclosure"

    insightMetrics = [
        {
            "title": "Happy Posts",
            "value": round((happy_count / total) * 100),
        },
        {
            "title": "Best Posting Time",
            "value": round((hour_buckets[best_time] / total) * 100),
            "label": best_time.capitalize(),
        },
        {
            "title": "Respectful Behavior",
            "value": round(avg_respect * 100),
        },
        {
            "title": "Privacy Behavior",
            "value": round((1 - avg_privacy) * 100),
            "label": privacy_profile,
        },
    ]

    recommendations = [
        {"text": "You frequently share positive experiences." if happy_count / total >= 0.5 else "Try sharing more uplifting moments."},
        {"text": f"Your engagement is strongest during the {best_time}."},
        {"text": "Your communication style is respectful." if avg_respect >= 0.7 else "Consider a calmer tone in discussions."},
        {"text": "You manage privacy responsibly." if avg_privacy < 0.4 else "Be cautious when sharing personal details."},
    ]

    return insightMetrics, recommendations
