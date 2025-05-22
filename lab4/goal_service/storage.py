from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["goal_db"]
goals_collection = db["goals"]