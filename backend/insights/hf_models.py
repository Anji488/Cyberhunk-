import logging
import os
import re
import requests
import time

logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

def query_hf_api(text, model_id):
    """Sends a request to the HF Inference API with wait_for_model enabled."""
    if not HF_TOKEN:
        logger.error("HUGGINGFACE_TOKEN is missing!")
        return None

    api_url = f"https://router.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # payload with wait_for_model: True handles the 503 'loading' state automatically
    payload = {
        "inputs": text,
        "options": {"wait_for_model": True}
    }

    try:
        if not text or not text.strip():
            return None

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"HF API Error {response.status_code}: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        logger.error(f"HF Request Failed for {model_id}: {e}")
        return None

def get_sentiment_model():
    return lambda text: query_hf_api(text, "Anjanie/roberta-sentiment")

def map_sentiment_label(label: str) -> str:
    mapping = {
        "negative": "negative", "neutral": "neutral", "positive": "positive",
        "LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"
    }
    return mapping.get(label, "neutral")

def get_toxic_model():
    return lambda text: query_hf_api(text, "Anjanie/distilbert-base-uncased-toxicity")

def get_misinfo_model():
    return lambda text: query_hf_api(text, "Anjanie/bert-base-uncased-misinformation")

def get_ner_model():
    return lambda text: query_hf_api(text, "dslim/bert-base-NER")

def extract_entities(text: str):
    ner_func = get_ner_model()
    locations = []
    
    try:
        entities = ner_func(text)
        if entities and isinstance(entities, list):
            for e in entities:
                # Flexible check for entity keys and LOC tags
                label = (e.get("entity") or e.get("entity_group") or "").upper()
                if "LOC" in label or "GPE" in label:
                    word = e.get("word", "").replace("##", "")
                    if word:
                        locations.append(word)
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")

    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text or "")
    phones = re.findall(r"\b\d{10,13}\b", text or "")

    return {
        "locations": list(set(locations)), 
        "emails": list(set(emails)), 
        "phones": list(set(phones))
    }