# backend/insights/gradio_models.py

from gradio_client import Client
import os
import logging
from functools import lru_cache

from insights.label_maps import SENTIMENT_MAP, TOXICITY_MAP, MISINFO_MAP

logger = logging.getLogger(__name__)
_client = None


# Emoji Sentiment

POS_EMOJIS = {"😍", "🥰", "❤️", "😂", "😊", "👍", "🥹", "🤩", "🤣"}
NEG_EMOJIS = {"😢", "💔", "😠", "😡", "😞", "😤", "🤥"}

def emoji_sentiment(text: str):
    text = text.strip()
    if not text:
        return None
    pos_count = sum(text.count(e) for e in POS_EMOJIS)
    neg_count = sum(text.count(e) for e in NEG_EMOJIS)
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return None


# Gradio Client

def get_gradio_client():
    global _client
    if _client is None:
        _client = Client(
            "Anjanie/cyberhunk",
            timeout=20 )  
        logger.info("Gradio client initialized WITHOUT auth (public Space).")
    return _client


def analyze_text_gradio(text: str) -> dict:
    """
    Normalized Gradio API output with emoji support
    """
    if not text or not text.strip():
        return {
            "label": "neutral",
            "toxic": False,
            "misinformation": False,
            "entities": [],
            "phones": [],
            "emails": [],
        }

    try:
        client = get_gradio_client()
        if not client:
            logger.warning("[GRADIO ERROR] Client not initialized.")
            return {}

        raw = client.predict(text=text[:2000], api_name="/analyze_text")
        if not isinstance(raw, dict):
            logger.warning(f"[GRADIO ERROR] Unexpected response type: {type(raw)}")
            return {}

        
        # Sentiment
        
        sentiment_raw = raw.get("sentiment")
        sentiment = SENTIMENT_MAP.get(sentiment_raw, "neutral")

        # Emoji override
        emoji_override = emoji_sentiment(text)
        if emoji_override:
            sentiment = emoji_override

        
        # Toxicity
        
        toxicity_raw = raw.get("toxicity")
        toxic = TOXICITY_MAP.get(toxicity_raw, False)

        
        # Misinformation
        
        misinfo_raw = raw.get("misinformation")
        misinformation = MISINFO_MAP.get(misinfo_raw, False)

        
        # Entities & Personal Info
        
        entities = raw.get("entities", [])
        phones = raw.get("phones", [])
        emails = raw.get("emails", [])

        return {
            "label": sentiment,
            "toxic": toxic,
            "misinformation": misinformation,
            "entities": entities,
            "phones": phones,
            "emails": emails,
        }

    except Exception as e:
        logger.error(f"[GRADIO ERROR] {e}", exc_info=True)
        return {
            "label": "neutral",
            "toxic": False,
            "misinformation": False,
            "entities": [],
            "phones": [],
            "emails": [],
            "error": "ml_unavailable"
        }

