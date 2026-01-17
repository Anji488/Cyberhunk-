import re
import logging
import os
import random
from datetime import datetime
import json
import requests

import pytz
from langdetect import detect, LangDetectException
from emoji import demojize, EMOJI_DATA

from openai import OpenAI

from insights import hf_models as insight_models
from insights.hf_models import map_sentiment_label

print(os.getenv("HUGGINGFACE_TOKEN"))

logger = logging.getLogger(__name__)

LOCAL_TZ = pytz.timezone("Asia/Colombo")

def remove_variation_selectors(text: str) -> str:
    """Remove emoji variation selectors (U+FE0F)."""
    return text.replace("\ufe0f", "")


def is_emoji_only(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and all(
        ch in EMOJI_DATA or ch.isspace() for ch in stripped
    )


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

    processed_text = demojize(clean_text)
    processed_text = processed_text.replace(":", " ").replace("_", " ")

    try:
        lang = detect(processed_text)
    except LangDetectException:
        lang = "en"

    translated_text = processed_text

    if lang != "en":
        try:
            from googletrans import Translator  
            translator = Translator()
            translated_text = translator.translate(
                processed_text, dest="en"
            ).text
        except Exception as e:
            logger.warning(f"[TRANSLATION FAILED] {e}")
            translated_text = processed_text

    label = "neutral"

    if method == "ml":
        sentiment_predictor = insight_models.get_sentiment_model()
        if sentiment_predictor:
            try:
                pred = sentiment_predictor(translated_text)
                
                if pred and isinstance(pred, list):
                    data = pred[0][0] if isinstance(pred[0], list) else pred[0]
                    raw_label = data.get("label", "")
                    score = float(data.get("score", 0))
                    mapped = map_sentiment_label(raw_label)

                    label = mapped if score >= 0.5 else mapped
            except Exception as e:
                logger.error(f"[SENTIMENT ERROR] {e}")

    return {
        "original": original_text,
        "translated": translated_text,
        "label": label,
    }


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


def generate_ai_recommendations_openai(insights, insightMetrics):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    filtered_insights = [
        item for item in insights
        if item.get("translated") and item["translated"].strip()
    ] or [{"translated": "User has a few short posts."}]

    prompt = f"""
You are a friendly AI assistant analyzing social media behavior.

User insight metrics:
{json.dumps(insightMetrics, indent=2)}

Sample analyzed posts:
{json.dumps(filtered_insights[:5], indent=2)}

Generate exactly 4 personalized digital wellbeing recommendations.

Rules:
- One sentence each
- Friendly and supportive
- Actionable
- No emojis
- No numbering
- One recommendation per line
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200,
        )

        text = response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"[OPENAI ERROR] {e}")
        return []

    recommendations = [
        {"text": line.strip()}
        for line in text.split("\n")
        if line.strip()
    ]

    return recommendations[:4]

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

    recommendations = generate_ai_recommendations_openai(insights, insightMetrics)

    return insightMetrics, recommendations

def fetch_profile(token):
    url = (
        f"https://graph.facebook.com/v19.0/me?"
        f"fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )
    res = requests.get(url, timeout=10)
    return res.json() if res.status_code == 200 else None
