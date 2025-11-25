import logging
import os
import re
from transformers.utils import logging as hf_logging

# ⚙️ Prevent heavy torchvision imports (Render memory saver)
os.environ["TRANSFORMERS_NO_TORCHVISION_IMPORT"] = "1"

logger = logging.getLogger(__name__)
hf_logging.set_verbosity_error()

# -----------------------------
# Cached pipelines
# -----------------------------
_sentiment_model = None
_toxic_model = None
_misinfo_model = None
_ner_model = None


# -----------------------------
# Lazy loader for Hugging Face pipelines
# -----------------------------
def _load_pipeline(task, model, **kwargs):
    """
    Lazy-load a Hugging Face pipeline only when needed.
    Ensures CPU compatibility and avoids meta tensor issues.
    """
    try:
        from transformers import pipeline, AutoModelForTokenClassification, AutoModelForSequenceClassification, AutoTokenizer
        import torch

        logger.info(f"🚀 Loading HF pipeline: {model}")

        device = -1  # CPU
        dtype = torch.float32  # avoid meta tensors

        # Special handling for token-classification pipelines
        if task == "token-classification":
            model_obj = AutoModelForTokenClassification.from_pretrained(
                model, dtype=dtype, device_map={"": "cpu"}
            )
            tokenizer = AutoTokenizer.from_pretrained(model)
            return pipeline(task, model=model_obj, tokenizer=tokenizer, **kwargs)
        else:
            return pipeline(task, model=model, device=device, **kwargs)

    except Exception as e:
        logger.error(f"❌ Failed to load pipeline '{model}': {e}")
        return None

# -----------------------------
# Sentiment model
# -----------------------------
def get_sentiment_model():
    global _sentiment_model
    if _sentiment_model is None:
        _sentiment_model = _load_pipeline(
            "sentiment-analysis", "Anjanie/roberta-sentiment"
        )
    return _sentiment_model


def map_sentiment_label(label: str) -> str:
    """Map model labels to simple human-readable sentiment names."""
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
# Toxicity model
# -----------------------------
def get_toxic_model():
    global _toxic_model
    if _toxic_model is None:
        _toxic_model = _load_pipeline(
            "text-classification", "Anjanie/distilbert-base-uncased-toxicity"
        )
    return _toxic_model


# -----------------------------
# Misinformation model
# -----------------------------
def get_misinfo_model():
    global _misinfo_model
    if _misinfo_model is None:
        _misinfo_model = _load_pipeline(
            "text-classification", "Anjanie/bert-base-uncased-misinformation"
        )
    return _misinfo_model


# -----------------------------
# NER model
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
# Entity extraction helper
# -----------------------------
def extract_entities(text: str):
    """
    Extract locations, emails, and phone numbers from text.
    """
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

    # Regex patterns for emails & phone numbers
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {"locations": locations, "emails": emails, "phones": phones}
