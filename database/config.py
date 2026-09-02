from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from core.config import get_settings

settings = get_settings()

# Create a new client and connect to the server
client = MongoClient(
    settings.database_url,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=5000,
)

db = client[settings.database_name]

# creating collections
profile_collection = db["profile"]
education_collection = db["education"]
skills_collection = db["skills"]
timeline_collection = db["timeline"]
project_collection = db["project"]
user_collection = db["user"]
