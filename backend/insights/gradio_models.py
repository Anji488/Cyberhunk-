# backend/insights/gradio_models.py

from gradio_client import Client
import logging

from insights.label_maps import SENTIMENT_MAP, TOXICITY_MAP, MISINFO_MAP

logger = logging.getLogger(__name__)
_client = None


# =========================
# Emoji Sentiment
# =========================

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


# =========================
# Gradio Client (SAFE)
# =========================

def get_gradio_client():
    """
    Singleton Gradio client.
    No init-time timeout (not supported in your version).
    """
    global _client
    if _client is None:
        _client = Client("Anjanie/cyberhunk")
        logger.info("Gradio client initialized (public HF Space).")
    return _client


# =========================
# Gradio Analysis
# =========================

def analyze_text_gradio(text: str) -> dict:
    """
    Calls HF Gradio Space safely with:
    - input size limit
    - request timeout
    - safe fallback response
    """

    # Default safe response
    default_response = {
        "label": "neutral",
        "toxic": False,
        "misinformation": False,
        "entities": [],
        "phones": [],
        "emails": [],
    }

    if not text or not text.strip():
        return default_response

    try:
        client = get_gradio_client()

        # HARD LIMIT input size (prevents slow inference & memory spikes)
        text = text.strip()[:2000]

        # IMPORTANT: timeout is applied HERE (supported)
        raw = client.predict(
            text=text,
            api_name="/analyze_text",
            timeout=20  # seconds
        )

        if not isinstance(raw, dict):
            logger.warning(
                "[GRADIO ERROR] Unexpected response type: %s",
                type(raw)
            )
            return default_response

        # -------- Sentiment --------
        sentiment_raw = raw.get("sentiment")
        sentiment = SENTIMENT_MAP.get(sentiment_raw, "neutral")

        # Emoji override
        emoji_override = emoji_sentiment(text)
        if emoji_override:
            sentiment = emoji_override

        # -------- Toxicity --------
        toxicity_raw = raw.get("toxicity")
        toxic = TOXICITY_MAP.get(toxicity_raw, False)

        # -------- Misinformation --------
        misinfo_raw = raw.get("misinformation")
        misinformation = MISINFO_MAP.get(misinfo_raw, False)

        # -------- Entities & Personal Info --------
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
        logger.error("[GRADIO ERROR] %s", e, exc_info=True)
        return {
            **default_response,
            "error": "ml_unavailable"
        }
