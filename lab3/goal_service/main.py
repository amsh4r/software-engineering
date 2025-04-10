from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List
from models import Goal
from config import SECRET_KEY, ALGORITHM
from storage import goals

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/token")  # URL user_service

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@app.post("/goals", response_model=Goal)
def create_goal(goal: Goal, current_user: str = Depends(get_current_user)):
    new_id = len(goals) + 1
    new_goal = Goal(id=new_id, title=goal.title, description=goal.description, deadline=goal.deadline)
    goals[new_id] = new_goal
    return new_goal

@app.get("/goals", response_model=List[Goal])
def get_goals(current_user: str = Depends(get_current_user)):
    return list(goals.values())

@app.get("/goals/{goal_id}", response_model=Goal)
def get_goal(goal_id: int, current_user: str = Depends(get_current_user)):
    if goal_id not in goals:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goals[goal_id]

@app.put("/goals/{goal_id}", response_model=Goal)
def update_goal(goal_id: int, updated_goal: Goal, current_user: str = Depends(get_current_user)):
    if goal_id not in goals:
        raise HTTPException(status_code=404, detail="Goal not found")
    goals[goal_id] = Goal(id=goal_id, title=updated_goal.title, description=updated_goal.description, deadline=updated_goal.deadline)
    return goals[goal_id]

@app.delete("/goals/{goal_id}", response_model=Goal)
def delete_goal(goal_id: int, current_user: str = Depends(get_current_user)):
    if goal_id not in goals:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goals.pop(goal_id)
