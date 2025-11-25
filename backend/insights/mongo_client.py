from pymongo import MongoClient
from urllib.parse import quote_plus

username = "anji"
password = quote_plus("3131270@Aki")  # encode special chars
cluster = "cluster0.6rpj2nc.mongodb.net"
database = "cyberhunk"

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["digital_responsibility"]
reports_collection = db["reports"]
