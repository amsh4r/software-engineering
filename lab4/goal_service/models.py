from pydantic import BaseModel
from typing import List, Optional

class Goal(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    members: List[int]