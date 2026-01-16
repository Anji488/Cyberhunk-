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

# TEXT NORMALIZATION

def remove_variation_selectors(text: str) -> str:
    """Remove emoji variation selectors (U+FE0F)."""
    return text.replace("\ufe0f", "")


def is_emoji_only(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and all(
        ch in EMOJI_DATA or ch.isspace() for ch in stripped
    )



# CORE NLP ANALYSIS

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

    
    # Emoji-only handling
    def emoji_sentiment_analysis(text: str) -> str:
        """
        Analyze any emoji or text+emoji sentiment using OpenAI.
        Returns: 'positive', 'neutral', or 'negative'
        """
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if not text or not text.strip():
            return "neutral"

        prompt = f"""
    Analyze the sentiment of the following text or emoji. 
    Return only one word: positive, neutral, or negative.

    Text/Emoji: {text}
    """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",   
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            label = response.choices[0].message.content.strip().lower()
            if label not in {"positive", "neutral", "negative"}:
                return "neutral"
            return label
        except Exception as e:
            logger.error(f"[OPENAI EMOJI ERROR] {e}")
            return "neutral"

    if is_emoji_only(clean_text):
        # Use OpenAI to detect sentiment of any emoji
        label = emoji_sentiment_analysis(clean_text)
        return {
            "original": original_text,
            "translated": original_text,
            "label": label,
        }
    
    # Emoji to text
    
    processed_text = demojize(clean_text)
    processed_text = processed_text.replace(":", " ").replace("_", " ")

    
    # Language detection
    
    try:
        lang = detect(processed_text)
    except LangDetectException:
        lang = "en"

    translated_text = processed_text

    
    # Lazy translation 
    
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

    
    # Sentiment ML
    
    label = "neutral"

    if method == "ml":
        sentiment_predictor = insight_models.get_sentiment_model()
        if sentiment_predictor:
            try:
                pred = sentiment_predictor(translated_text)
                
                # API returns [[{'label': '...', 'score': ...}]]
                if pred and isinstance(pred, list):
                    # Handle nested list or single list response
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



# LOCATION DETECTION

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



# TOXICITY

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
                data = pred[0][0] if isinstance(pred[0], list) else pred[0]
                label = str(data.get("label", "")).lower()
                # Check for 'toxic' label or high scores in specific labels
                model_prediction = "toxic" in label or label == "label_1"
        except Exception as e:
            logger.error(f"[TOXIC MODEL ERROR] {e}")

    return keyword_match or model_prediction


def is_respectful(text: str) -> bool:
    return not is_toxic(text)



# PRIVACY

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



# MISINFORMATION

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


# METRICS & RECOMMENDATIONS
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

def percentile(values, percent):
    """Return the percentile value from a list (0-1 scale)."""
    if not values:
        return 0
    values = sorted(values)
    k = (len(values)-1) * percent / 100
    f = int(k)
    c = min(f+1, len(values)-1)
    d0 = values[f] * (c-k)
    d1 = values[c] * (k-f)
    return d0 + d1

def percentile(values, percent):
    """Return the percentile value from a sorted list."""
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * percent / 100
    f = int(k)
    c = min(f + 1, len(values) - 1)
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return d0 + d1


def percentile_metric(values, invert=False):
    """Compute percentile-based metric with min-max scaling, safely."""
    if not values:
        return 0

    # Convert boolean/binary values to float
    values_float = [float(v) for v in values]

    # 90th percentile
    p90 = percentile(values_float, 90)
    min_val = min(values_float)
    max_val = max(values_float)

    # Avoid divide by zero
    if max_val != min_val:
        score = (p90 - min_val) / (max_val - min_val)
    else:
        score = p90

    if invert:
        score = 1 - score

    return round(score * 100)


def compute_insight_metrics(insights: list):
    positive_list = []
    night_list = []
    location_list = []
    respectful_list = []

    for item in insights:
        label = (item.get("label") or "").lower()
        positive_list.append(1 if label == "positive" else 0)

        ts = item.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                local_dt = dt.astimezone(LOCAL_TZ)
                night_list.append(1 if local_dt.hour >= 23 or local_dt.hour < 6 else 0)
            except Exception:
                night_list.append(0)
        else:
            night_list.append(0)

        location_list.append(1 if item.get("mentions_location") else 0)
        respectful_list.append(1 if item.get("is_respectful") else 0)

    insightMetrics = [
        {"title": "Happy Posts", "value": percentile_metric(positive_list)},
        {"title": "Good Posting Habits", "value": percentile_metric(night_list, invert=True)},
        {"title": "Privacy Care", "value": percentile_metric(location_list, invert=True)},
        {"title": "Being Respectful", "value": percentile_metric(respectful_list)},
    ]

    # Generate recommendations safely
    try:
        recommendations = generate_ai_recommendations_openai(insights, insightMetrics)
    except Exception as e:
        logger.error(f"[RECOMMENDATION FAILED] {e}")
        recommendations = []

    return insightMetrics, recommendations



def fetch_profile(token):
    url = (
        f"https://graph.facebook.com/v19.0/me?"
        f"fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )
    res = requests.get(url, timeout=10)
    return res.json() if res.status_code == 200 else None
