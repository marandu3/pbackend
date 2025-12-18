from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    username:str
    password:str

class UserCreate(User):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

    