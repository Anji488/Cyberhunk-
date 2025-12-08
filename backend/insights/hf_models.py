import logging
import os
import re

# Prevent heavy torchvision import (optional but safe)
os.environ["TRANSFORMERS_NO_TORCHVISION_IMPORT"] = "1"

logger = logging.getLogger(__name__)

# Cached pipelines
_sentiment_model = None
_toxic_model = None
_misinfo_model = None
_ner_model = None


# -----------------------------
# Lazy loader for Hugging Face pipelines
# -----------------------------
def _load_pipeline(task, model, **kwargs):
    """
    Lazily load HF pipeline only when needed.
    ALL heavy imports are inside this function.
    Prevents Render from crashing on startup.
    """
    try:
        from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
        import torch

        logger.info(f"🚀 Loading HF pipeline: {model}")

        # Handle token-classification (NER)
        if task == "token-classification":
            model_obj = AutoModelForTokenClassification.from_pretrained(
                model,
                torch_dtype=torch.float32,
                device_map=None  # CPU-only
            )
            tokenizer = AutoTokenizer.from_pretrained(model)
            return pipeline(task, model=model_obj, tokenizer=tokenizer, **kwargs)

        # Normal pipelines (sentiment, toxicity, misinformation)
        return pipeline(task, model=model, device=-1, **kwargs)

    except Exception as e:
        logger.error(f"❌ Failed to load pipeline '{model}': {e}")
        return None


# -----------------------------
# Sentiment Model
# -----------------------------
def get_sentiment_model():
    global _sentiment_model
    if _sentiment_model is None:
        _sentiment_model = _load_pipeline(
            "sentiment-analysis",
            "Anjanie/roberta-sentiment"
        )
    return _sentiment_model


def map_sentiment_label(label: str) -> str:
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


# -----------------------------
# Toxicity Model
# -----------------------------
def get_toxic_model():
    global _toxic_model
    if _toxic_model is None:
        _toxic_model = _load_pipeline(
            "text-classification",
            "Anjanie/distilbert-base-uncased-toxicity"
        )
    return _toxic_model


# -----------------------------
# Misinformation Model
# -----------------------------
def get_misinfo_model():
    global _misinfo_model
    if _misinfo_model is None:
        _misinfo_model = _load_pipeline(
            "text-classification",
            "Anjanie/bert-base-uncased-misinformation"
        )
    return _misinfo_model


# -----------------------------
# NER Model
# -----------------------------
def get_ner_model():
    global _ner_model
    if _ner_model is None:
        _ner_model = _load_pipeline(
            "token-classification",
            "dslim/bert-base-NER",
            aggregation_strategy="simple",
        )
    return _ner_model


# -----------------------------
# Entity Extraction Helper
# -----------------------------
def extract_entities(text: str):
    ner = get_ner_model()
    if not ner:
        return {"locations": [], "emails": [], "phones": []}

    try:
        entities = ner(text)
        locations = [
            e["word"]
            for e in entities
            if e.get("entity_group") in ["LOC", "GPE"]
        ]
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")
        locations = []

    # Regex for email & phone
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {"locations": locations, "emails": emails, "phones": phones}
