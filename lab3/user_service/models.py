from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from db import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=True)

    def set_password(self, password: str):
        """Хеширует и сохраняет пароль."""
        self.hashed_password = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        """Проверяет пароль."""
        return pwd_context.verify(password, self.hashed_password)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    age: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int] = None

    class Config:
        from_attributes = True  

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
