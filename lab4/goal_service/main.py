from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from bson import ObjectId
from typing import List
from models import Goal
from storage import goals_collection
from config import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_user_in_goal(goal: dict, user_id: int):
    if user_id not in goal.get("members", []):
        raise HTTPException(status_code=403, detail="User is not a member of this goal")

@app.post("/goals", response_model=Goal)
def create_goal(goal: Goal, current_user: dict = Depends(get_current_user)):
    goal_dict = goal.dict(exclude={"id"})
    if current_user["id"] not in goal_dict.get("members", []):
        goal_dict["members"] = goal_dict.get("members", []) + [current_user["id"]]
    result = goals_collection.insert_one(goal_dict)
    goal.id = str(result.inserted_id)
    return goal

@app.get("/goals", response_model=List[Goal])
def get_goals(current_user: dict = Depends(get_current_user)):
    goals = []
    for goal in goals_collection.find({"members": current_user["id"]}):
        goal["id"] = str(goal["_id"])
        del goal["_id"]
        goals.append(Goal(**goal))
    return goals

@app.get("/goals/{goal_id}", response_model=Goal)
def get_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    goal = goals_collection.find_one({"_id": ObjectId(goal_id)})
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    check_user_in_goal(goal, current_user["id"])
    goal["id"] = str(goal["_id"])
    del goal["_id"]
    return Goal(**goal)

@app.put("/goals/{goal_id}", response_model=Goal)
def update_goal(goal_id: str, updated_goal: Goal, current_user: dict = Depends(get_current_user)):
    goal = goals_collection.find_one({"_id": ObjectId(goal_id)})
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    check_user_in_goal(goal, current_user["id"])
    result = goals_collection.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": updated_goal.dict(exclude={"id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    updated_goal.id = goal_id
    return updated_goal

@app.delete("/goals/{goal_id}", response_model=Goal)
def delete_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    goal = goals_collection.find_one({"_id": ObjectId(goal_id)})
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    check_user_in_goal(goal, current_user["id"])
    goals_collection.delete_one({"_id": ObjectId(goal_id)})
    goal["id"] = str(goal["_id"])
    del goal["_id"]
    return Goal(**goal)

@app.get("/goals/search/by-name", response_model=List[Goal])
def search_goals_by_name(name: str, current_user: dict = Depends(get_current_user)):
    goals = []
    query = {"name": {"$regex": name, "$options": "i"}, "members": current_user["id"]}
    for goal in goals_collection.find(query):
        goal["id"] = str(goal["_id"])
        del goal["_id"]
        goals.append(Goal(**goal))
    if not goals:
        raise HTTPException(status_code=404, detail="No goals found with this name")
    return goals