# backend/insights/mongo_client.py
from pymongo import MongoClient
from urllib.parse import quote_plus
import os

username = os.getenv("MONGO_USER", "anji")
password = quote_plus(os.getenv("MONGO_PASS", "3131270@Aki"))
cluster = os.getenv("MONGO_CLUSTER", "cluster0.6rpj2nc.mongodb.net")
database = os.getenv("MONGO_DB", "digital_responsibility")  

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client[database]
reports_collection = db["reports"]
