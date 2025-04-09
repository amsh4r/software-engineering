from pydantic import BaseModel
from datetime import date

class Goal(BaseModel):
    id: int
    title: str
    description: str
    deadline: date
    owner: str  
