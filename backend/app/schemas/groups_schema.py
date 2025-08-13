from pydantic import BaseModel
from datetime import datetime
from app.models.messages import GroupChat
from app.schemas.users_schemas import User

class GroupChatBase(BaseModel):
    name:str


class GroupChatCreate(GroupChatBase):
    members : list[int] | None = []


class GroupChatDisplay(GroupChatBase):
    id:int
    owner_id:int
    created_at:datetime
    members:list[User]

    class Config:
        from_attributes = True


class GroupUpdate(GroupChatBase):
    name : str | None = None