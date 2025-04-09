from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import List
from models import User, Token
from storage import users, pwd_context
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from auth import get_current_user, create_access_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    for user in users.values():
        if user.username == form_data.username and pwd_context.verify(form_data.password, user.hashed_password):
            password_check = True
            break
    if not password_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_user)):
    if any(u.username == user.username for u in users.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    new_id = len(users) + 1
    hashed_password = pwd_context.hash(user.hashed_password)
    new_user = User(id=new_id, username=user.username, email=user.email, hashed_password=hashed_password, age=user.age)
    users[new_id] = new_user
    return new_user

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, current_user: str = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.get("/users", response_model=List[User])
def get_users(current_user: User = Depends(get_current_user)):
    return list(users.values())

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, current_user: str = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if updated_user.username != users[user_id].username and any(u.username == updated_user.username for u in users.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(updated_user.hashed_password)
    users[user_id] = User(id=user_id, username=updated_user.username, email=updated_user.email, hashed_password=hashed_password)
    return users[user_id]

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = users.pop(user_id)
    return deleted_user