import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from db import Base
from models import User

DATABASE_URL = "postgresql://alex:password@db:5432/my_user_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def wait_for_db():
    while True:
        try:
            with engine.connect() as conn:
                print("База данных доступна!")
                break
        except OperationalError:
            print("Ожидание базы данных...")
            time.sleep(2)

def init_db():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            users = [
                {"username": "admin", "email": "admin@localhost", "password": "secret", "age": None},
                {"username": "aleksei", "email": "aleksei@example.com", "password": "strongpass", "age": 22},
                {"username": "devguy", "email": "dev@example.com", "password": "code123", "age": 26},
                {"username": "testuser", "email": "test@example.com", "password": "testing", "age": 30}
            ]

            for u in users:
                user = User(username=u["username"], email=u["email"], age=u["age"])
                user.set_password(u["password"])
                db.add(user)

            db.commit()
            print("Инициализация пользователей завершена.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
