import logging
import os
import re
import requests
import time

# Prevent heavy torchvision import (optional but safe)
os.environ["TRANSFORMERS_NO_TORCHVISION_IMPORT"] = "1"

logger = logging.getLogger(__name__)

# --- API CONFIGURATION ---
# Get your token from https://huggingface.co/settings/tokens
# Set this in Render Environment Variables as HUGGINGFACE_TOKEN
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# Cached results (optional, for the session)
_sentiment_model = None
_toxic_model = None
_misinfo_model = None
_ner_model = None

def query_hf_api(text, model_id):
    """Sends a request to the HF Inference API instead of loading model locally."""
    if not HF_TOKEN:
        logger.error("❌ HUGGINGFACE_TOKEN is missing! Please set it in Render environment variables.")
        return None

    api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)
        
        # Handle 503 error (Model loading on HF side)
        if response.status_code == 503:
            logger.info(f"⏳ Model {model_id} is waking up, waiting 3s...")
            time.sleep(3)
            response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)
            
        if response.status_code != 200:
            logger.error(f"❌ HF API Error {response.status_code}: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        logger.error(f"❌ HF Request Failed for {model_id}: {e}")
        return None

# -----------------------------
# Sentiment Model
# -----------------------------
def get_sentiment_model():
    # Returns a lambda that mimics the old pipeline behavior
    return lambda text: query_hf_api(text, "Anjanie/roberta-sentiment")

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
    return lambda text: query_hf_api(text, "Anjanie/distilbert-base-uncased-toxicity")

# -----------------------------
# Misinformation Model
# -----------------------------
def get_misinfo_model():
    return lambda text: query_hf_api(text, "Anjanie/bert-base-uncased-misinformation")

# -----------------------------
# NER Model
# -----------------------------
def get_ner_model():
    return lambda text: query_hf_api(text, "dslim/bert-base-NER")

# -----------------------------
# Entity Extraction Helper (Kept your logic)
# -----------------------------
def extract_entities(text: str):
    ner_func = get_ner_model()
    locations = []
    
    try:
        entities = ner_func(text)
        if entities and isinstance(entities, list):
            # API response handling
            for e in entities:
                # Check for location tags in entity_group or entity
                group = e.get("entity_group") or e.get("entity") or ""
                if any(loc_tag in group.upper() for loc_tag in ["LOC", "GPE"]):
                    locations.append(e.get("word", ""))
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")

    # Regex for email & phone (Your existing logic)
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10}\b"

    emails = re.findall(email_pattern, text or "")
    phones = re.findall(phone_pattern, text or "")

    return {"locations": list(set(locations)), "emails": emails, "phones": phones}