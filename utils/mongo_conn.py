from pymongo import MongoClient

from config import MONGO

def get_mongo_connection():
    host = MONGO['mongo_host']
    username = MONGO['mongo_user']
    password = MONGO['mongo_pass']
    client = MongoClient(host, 27017,
        username=username, password=password)

    return client

def get_mongo_db(db_name=MONGO['mongo_db']):
    client = get_mongo_connection()
    return client[db_name]