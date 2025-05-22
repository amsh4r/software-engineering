import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from storage import goals_collection
from models import Goal

MONGO_URL = "mongodb://mongo:27017/"

def wait_for_mongo():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    while True:
        try:
            client.admin.command("ping")
            print("MongoDB доступен!")
            break
        except ConnectionFailure:
            print("Ожидание MongoDB...")
            time.sleep(2)
        finally:
            client.close()

def init_db():
    wait_for_mongo()

    if goals_collection.count_documents({}) == 0:
        test_goals = [
            Goal(name="Goal 1", description="First test goal", members=[1, 2]),
            Goal(name="Goal 2", description="Second test goal", members=[1, 2, 3]),
        ]
        for goal in test_goals:
            goals_collection.insert_one(goal.dict())
        print("Test goals inserted successfully.")

    goals_collection.create_index("name")
    goals_collection.create_index("members")
    print("Indexes created on 'name' and 'members'.")

if __name__ == "__main__":
    init_db()