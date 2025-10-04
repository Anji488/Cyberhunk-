import os
import joblib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Path to models directory
MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models")

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

# Load models once at startup
sentiment_model = load_model("sentiment_dataset_model.pkl")
toxic_model = load_model("toxic_model.pkl")
misinfo_model = load_model("misinformations_model.pkl")
locations_model = load_model("locations_model.pkl")