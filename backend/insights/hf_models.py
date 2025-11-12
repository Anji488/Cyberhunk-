# backend/insights/hf_models.py

from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Model pipelines (cached)
# -----------------------------
_sentiment_model = None
_toxic_model = None
_misinfo_model = None
_ner_model = None  # For locations, phone, email detection

def get_sentiment_model():
    global _sentiment_model
    if _sentiment_model is None:
        try:
            model_name = "Anjanie/roberta-sentiment"
            _sentiment_model = pipeline("sentiment-analysis", model=model_name)
            logger.info(f"Loaded sentiment model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            _sentiment_model = None
    return _sentiment_model


# Add this helper mapping
def map_sentiment_label(label: str) -> str:
    """
    Convert model-specific labels to readable form.
    Adjust mapping based on your Hugging Face model card.
    """
    mapping = {
        "LABEL_0": "negative",
        "LABEL_1": "neutral",
        "LABEL_2": "positive",
        "label_0": "negative",
        "label_1": "neutral",
        "label_2": "positive",
        "NEGATIVE": "negative",
        "NEUTRAL": "neutral",
        "POSITIVE": "positive",
    }
    return mapping.get(label.strip(), label.lower())


def get_toxic_model():
    global _toxic_model
    if _toxic_model is None:
        try:
            _toxic_model = pipeline("text-classification", model="Anjanie/distilbert-base-uncased-toxicity")
            logger.info("Loaded toxicity model")
        except Exception as e:
            logger.error(f"Failed to load toxic model: {e}")
            _toxic_model = None
    return _toxic_model

def get_misinfo_model():
    global _misinfo_model
    if _misinfo_model is None:
        try:
            _misinfo_model = pipeline("text-classification", model="Anjanie/bert-base-uncased-misinformation")
            logger.info("Loaded misinformation model")
        except Exception as e:
            logger.error(f"Failed to load misinfo model: {e}")
            _misinfo_model = None
    return _misinfo_model

def get_ner_model():
    global _ner_model
    if _ner_model is None:
        try:
            _ner_model = pipeline("token-classification", model="dslim/bert-base-NER", aggregation_strategy="simple")
            logger.info("Loaded NER model")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            _ner_model = None
    return _ner_model

# -----------------------------
# Helper NER detection
# -----------------------------
def extract_entities(text):
    """Return detected locations, emails, phones from text"""
    ner = get_ner_model()
    if not ner:
        return {"locations": [], "emails": [], "phones": []}

    try:
        entities = ner(text)
        locations = [e['word'] for e in entities if e['entity_group'] in ['LOC', 'GPE']]
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")
        locations = []

    # Simple regex for emails & phones
    import re
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {"locations": locations, "emails": emails, "phones": phones}
