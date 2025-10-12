import os
import joblib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Path to models directory
MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models")

# Model references
_sentiment_model = None
_toxic_model = None
_misinfo_model = None
_locations_model = None

def load_model(filename):
    path = os.path.join(MODEL_PATH, filename)
    if not os.path.exists(path):
        logger.warning(f"Model file not found: {filename}")
        return None
    try:
        model = joblib.load(path)
        logger.info(f"Loaded model: {filename}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model {filename}: {e}")
        return None

def get_sentiment_model():
    global _sentiment_model
    if _sentiment_model is None:
        _sentiment_model = load_model("sentiment_dataset_model.pkl")
    return _sentiment_model

def get_toxic_model():
    global _toxic_model
    if _toxic_model is None:
        _toxic_model = load_model("toxic_model.pkl")
    return _toxic_model

def get_misinfo_model():
    global _misinfo_model
    if _misinfo_model is None:
        _misinfo_model = load_model("misinformations_model.pkl")
    return _misinfo_model

def get_locations_model():
    global _locations_model
    if _locations_model is None:
        _locations_model = load_model("locations_model.pkl")
    return _locations_model
