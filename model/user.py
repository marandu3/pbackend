from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    role: str = "admin"

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
