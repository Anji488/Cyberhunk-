from gradio_client import Client
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from insights.label_maps import SENTIMENT_MAP, TOXICITY_MAP, MISINFO_MAP

logger = logging.getLogger(__name__)
_client = None

# Thread pool for enforcing timeouts
_executor = ThreadPoolExecutor(max_workers=1)

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
# Gradio Client
# =========================

def get_gradio_client():
    global _client
    if _client is None:
        _client = Client("Anjanie/cyberhunk")
        logger.info("Gradio client initialized (public HF Space)")
    return _client


# =========================
# Internal call (NO timeout)
# =========================

def _predict_gradio(text: str):
    client = get_gradio_client()
    return client.predict(
        text=text,
        api_name="/analyze_text"
    )


# =========================
# Public Safe API
# =========================

def analyze_text_gradio(text: str) -> dict:
    """
    Safe Gradio inference with:
    - Hard timeout
    - Input size limit
    - Guaranteed response shape
    """

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

    # HARD input limit
    text = text.strip()[:2000]

    try:
        future = _executor.submit(_predict_gradio, text)

        try:
            raw = future.result(timeout=20)  # ⬅️ HARD TIMEOUT
        except TimeoutError:
            logger.error("[GRADIO TIMEOUT] Inference exceeded 20s")
            future.cancel()
            return {
                **default_response,
                "error": "ml_timeout"
            }

        if not isinstance(raw, dict):
            logger.warning("[GRADIO ERROR] Unexpected response type: %s", type(raw))
            return default_response

        # -------- Sentiment --------
        sentiment_raw = raw.get("sentiment")
        sentiment = SENTIMENT_MAP.get(sentiment_raw, "neutral")

        emoji_override = emoji_sentiment(text)
        if emoji_override:
            sentiment = emoji_override

        # -------- Toxicity --------
        toxicity_raw = raw.get("toxicity")
        toxic = TOXICITY_MAP.get(toxicity_raw, False)

        # -------- Misinformation --------
        misinfo_raw = raw.get("misinformation")
        misinformation = MISINFO_MAP.get(misinfo_raw, False)

        # -------- Entities --------
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
            "error": "ml_failure"
        }
