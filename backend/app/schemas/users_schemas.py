from pydantic import BaseModel
from app.models.users import User
from typing import Optional

class UserBase(BaseModel):
    username : str
    email : str
    



class UserCreate(UserBase):
    password : str

class UserUpdate(UserBase):
    username : Optional[str] = None
    email : Optional[str] = None

class UserDisplay(UserBase):
    id : int
    is_active : bool
    xp : int
    level : int
    pfp : str | None = None



class User(UserDisplay):
    class Config:
        from_attributes = True