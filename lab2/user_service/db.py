from passlib.context import CryptContext
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {
    1: User(
        id=1,
        username="admin",
        email="admin@example.com",
        hashed_password=pwd_context.hash("secret"),
        age=30
    )
}
