
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv


load_dotenv()

uri = os.getenv("DATABASE_URL")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

#creating the db
db =client['pmng']

#creating collections
profile_collection = db['profile']
education_collection = db['education']
skills_collection = db['skills']
timeline_collection = db['timeline']
project_collection = db['project']
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
