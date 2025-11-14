# insights/model_loader.py
import spacy
from transformers import pipeline

print("Loading NLP models at startup...")

# Load Spacy once
nlp = spacy.load("en_core_web_sm")

# Hugging Face sentiment pipeline (CPU)
sentiment_model = pipeline("sentiment-analysis")

print("Models loaded!")
