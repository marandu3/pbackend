
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# import os
# from dotenv import load_dotenv


# load_dotenv()

# uri = os.getenv("DATABASE_URL")

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# #creating the db
# db =client['pmng']

# #creating collections
# project_collection = db['project']
# skills_collection = db['skills']
# user_collection = db['skills']
# contacts_collection = db['contacts']

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)



from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# ✅ Use DB name in URI
uri = "mongodb+srv://johnwillymarandu:marandu1990@cluster0.2lxmfyt.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Error:", e)

# Use your database
db = client['pmng']

# Collections
project_collection = db['project']
skills_collection = db['skills']
user_collection = db['users']   # ⚠️ you had 'skills' twice before
contacts_collection = db['contacts']
