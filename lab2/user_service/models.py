from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
