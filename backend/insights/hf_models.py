import logging
import os
import re
import requests
import time

# Prevent heavy torchvision import
os.environ["TRANSFORMERS_NO_TORCHVISION_IMPORT"] = "1"

logger = logging.getLogger(__name__)

# --- API CONFIGURATION ---
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

def query_hf_api(text, model_id):
    """Sends a request to the HF Inference API."""
    if not HF_TOKEN:
        logger.error("HUGGINGFACE_TOKEN is missing! Set it in Render environment variables.")
        return None

    # New Router URL for Hugging Face Inference Providers
    api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        # Check for empty text to avoid API errors
        if not text or not text.strip():
            return None

        response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)
        
        # Handle 503 (Model Loading)
        if response.status_code == 503:
            logger.info(f"⏳ Model {model_id} is waking up, retrying in 5s...")
            time.sleep(5)
            response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)
            
        if response.status_code == 403:
            logger.error(f"HF API Error 403: Insufficient permissions for {model_id}. Check your token scopes (Inference API).")
            return None
            
        if response.status_code != 200:
            logger.error(f"HF API Error {response.status_code}: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        logger.error(f"HF Request Failed for {model_id}: {e}")
        return None


# Sentiment Model (Public/Stable)

def get_sentiment_model():
    # Industry standard for social media sentiment
    return lambda text: query_hf_api(text, "Anjanie/roberta-sentiment")

def map_sentiment_label(label: str) -> str:
    # CardiffNLP uses specific labels: 0->Negative, 1->Neutral, 2->Positive
    mapping = {
        "negative": "negative",
        "neutral": "neutral",
        "positive": "positive",
        "LABEL_0": "negative",
        "LABEL_1": "neutral",
        "LABEL_2": "positive"
    }
    return mapping.get(label, "neutral")


# Toxicity Model (Public/Stable)

def get_toxic_model():
    # The most popular public model for identifying toxic behavior
    return lambda text: query_hf_api(text, "Anjanie/distilbert-base-uncased-toxicity")


# Misinformation Model (Public/Stable)

def get_misinfo_model():
    # Good general-purpose fake news/misinfo detector
    return lambda text: query_hf_api(text, "Anjanie/bert-base-uncased-misinformation")


# NER Model (Locations/Privacy)

def get_ner_model():
    return lambda text: query_hf_api(text, "dslim/bert-base-NER")


# Entity Extraction Helper

def extract_entities(text: str):
    ner_func = get_ner_model()
    locations = []
    
    try:
        entities = ner_func(text)
        # BERT-NER returns a list of dictionaries if successful
        if entities and isinstance(entities, list):
            for e in entities:
                # API uses 'entity' or 'entity_group'
                label = e.get("entity", "") or e.get("entity_group", "")
                if any(loc_tag in label.upper() for loc_tag in ["LOC", "GPE"]):
                    locations.append(e.get("word", "").replace("##", ""))
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")

    # Regex for PII (Personal Identifiable Information)
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{10,13}\b" # Adjusted for international formats

    emails = re.findall(email_pattern, text or "")
    phones = re.findall(phone_pattern, text or "")

    return {
        "locations": list(set(locations)), 
        "emails": list(set(emails)), 
        "phones": list(set(phones))
    }