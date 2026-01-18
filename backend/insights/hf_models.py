import logging
import os
import re
import requests
import time
from dotenv import load_dotenv

# Load .env for local dev
load_dotenv()

os.environ["TRANSFORMERS_NO_TORCHVISION_IMPORT"] = "1"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    logger.warning("⚠️ HUGGINGFACE_TOKEN is missing! Private model API calls will fail.")

# -----------------------------
# HF API query helper
# -----------------------------
def query_hf_api(text: str, model_id: str):
    if not HF_TOKEN:
        logger.error("❌ HUGGINGFACE_TOKEN missing!")
        return None

    if not text or not text.strip():
        return None

    # Use private API endpoint for private models
    api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)

        if response.status_code == 503:
            logger.info(f"⏳ Model {model_id} is loading, retrying in 5s...")
            time.sleep(5)
            response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)

        if response.status_code == 403:
            logger.error(f"❌ HF API Error 403: Insufficient permissions for {model_id}.")
            return None

        if response.status_code == 404:
            logger.error(f"❌ HF API Error 404: Model {model_id} not found. Check ID & token access.")
            return None

        if response.status_code != 200:
            logger.error(f"❌ HF API Error {response.status_code}: {response.text}")
            return None

        return response.json()

    except Exception as e:
        logger.error(f"❌ HF request failed for {model_id}: {e}")
        return None

# -----------------------------
# Sentiment Model
# -----------------------------
def get_sentiment_model():
    return lambda text: query_hf_api(text, "Anjanie/roberta-sentiment")

def map_sentiment_label(label: str) -> str:
    mapping = {
        "negative": "negative",
        "neutral": "neutral",
        "positive": "positive",
        "LABEL_0": "negative",
        "LABEL_1": "neutral",
        "LABEL_2": "positive"
    }
    return mapping.get(label, "neutral")

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
# Entity Extraction Helper
# -----------------------------
def extract_entities(text: str):
    ner_func = get_ner_model()
    locations = []

    try:
        entities = ner_func(text)
        if entities and isinstance(entities, list):
            for e in entities:
                label = e.get("entity", "") or e.get("entity_group", "")
                if any(loc_tag in label.upper() for loc_tag in ["LOC", "GPE"]):
                    locations.append(e.get("word", "").replace("##", ""))
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")

    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10,13}\b"

    emails = re.findall(email_pattern, text or "")
    phones = re.findall(phone_pattern, text or "")

    return {
        "locations": list(set(locations)),
        "emails": list(set(emails)),
        "phones": list(set(phones))
    }
