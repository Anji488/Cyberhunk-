import re
import logging
import os
import random
from datetime import datetime
import json
import requests

import numpy as np
import pytz
from dateutil import parser
from langdetect import detect
from emoji import demojize, EMOJI_DATA

from openai import OpenAI

from insights.gradio_models import analyze_text_gradio
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
    if not text or not text.strip():
        return {
            "original": text,
            "translated": text,
            "label": "neutral",
        }

    result = analyze_text_gradio(text)

    return {
        "original": text,
        "translated": text,
        "label": result.get("label", "neutral"),
    }


# LOCATION DETECTION

def mentions_location(text: str):
    result = analyze_text_gradio(text)
    for ent in result.get("entities", []):
        if ent.get("entity") == "LOCATION":
            return ent.get("word")
    return None



# TOXICITY (Updated for API)

def is_toxic(text: str) -> bool:
    result = analyze_text_gradio(text)
    return bool(result.get("toxic", False))


def is_respectful(text: str) -> bool:
    return not is_toxic(text)



# PRIVACY
def discloses_personal_info(text: str) -> bool:
    result = analyze_text_gradio(text)
    return bool(result.get("phones") or result.get("emails"))




# MISINFORMATION (Updated for API)

def is_potential_misinformation(text: str) -> bool:
    result = analyze_text_gradio(text)
    return bool(result.get("misinformation", False))



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
 
Provide highly detailed analysis and recommendations to help the user improve their online presence using at least 5 paragraphs.
"""
 
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            # max_tokens=200,
        )
 
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        logger.error(f"[OPENAI ERROR] {e}")
        return ""

def compute_insight_metrics(insights: list):
    posts = [i for i in insights if i.get("type") == "post"]
    total_posts = len(posts)
    total_items = max(len(insights), 1)

    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    night_posts = 0
    location_mentions = 0
    respectful_count = 0

    
    # Sentiment & behavior (ALL)
    
    for item in insights:
        label = (item.get("label") or "").lower()
        if label in sentiment_counts:
            sentiment_counts[label] += 1

        if item.get("mentions_location"):
            location_mentions += 1

        if item.get("is_respectful"):
            respectful_count += 1

    
    # Posting habits (POSTS ONLY)
    
    for post in posts:
        ts = post.get("timestamp")
        if not ts:
            continue

        try:
            dt = parser.isoparse(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)

            local_dt = dt.astimezone(LOCAL_TZ)

            if local_dt.hour >= 23 or local_dt.hour < 6:
                night_posts += 1

        except Exception as e:
            logger.warning(f"Timestamp parse failed: {ts} | {e}")

    
    # Metric Calculations
    

    happy_posts_score = round(
        (sentiment_counts["positive"] / total_items) * 100
    )

    if total_posts == 0:
        good_posting_habits_score = 100
    else:
        late_ratio = night_posts / total_posts

        # Winsorized bounds (tunable)
        LOWER = 0.05   # ~90th percentile good users
        UPPER = 0.60   # heavy late-night posters

        late_ratio = max(LOWER, min(late_ratio, UPPER))

        normalized = 1 - ((late_ratio - LOWER) / (UPPER - LOWER))
        good_posting_habits_score = round(normalized * 100)

    privacy_care_score = round(
        100 - (location_mentions / total_items) * 100
    )

    respectful_score = round(
        (respectful_count / total_items) * 100
    )

    insightMetrics = [
        {"title": "Happy Posts", "value": happy_posts_score},
        {"title": "Good Posting Habits", "value": good_posting_habits_score},
        {"title": "Privacy Care", "value": privacy_care_score},
        {"title": "Being Respectful", "value": respectful_score},
    ]

    recommendations = generate_ai_recommendations_openai(
        insights,
        insightMetrics
    )

    return insightMetrics, recommendations


def fetch_profile(token):
    url = (
        f"https://graph.facebook.com/v19.0/me?"
        f"fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )
    res = requests.get(url, timeout=10)
    return res.json() if res.status_code == 200 else None
