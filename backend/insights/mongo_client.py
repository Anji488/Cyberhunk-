from pymongo import MongoClient
from urllib.parse import quote_plus
import os
import logging

logger = logging.getLogger(__name__)

username = os.getenv("MONGO_USER", "anji")
password = quote_plus(os.getenv("MONGO_PASS", "3131270@Aki"))
cluster = os.getenv("MONGO_CLUSTER", "cluster0.6rpj2nc.mongodb.net")
database = os.getenv("MONGO_DB", "digital_responsibility")

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority"

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000  # ⏱ force fast failure
    )

    # 🔥 FORCE CONNECTION
    client.admin.command("ping")
    logger.info("✅ MongoDB CONNECTED")

except Exception as e:
    logger.error(f"❌ MongoDB CONNECTION FAILED: {e}")
    raise  # VERY IMPORTANT

db = client[database]
reports_collection = db["reports"]
