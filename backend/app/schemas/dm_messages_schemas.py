from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class DmMessageDisplay(BaseModel):
    id : int
    content : str
    sender_id : int
    recipient_id : int
    timestamp : datetime
    is_read : bool
    parent_message_id : Optional[int] = None

    class Config:
        from_attributes = True

class GroupMesssageDisplay(BaseModel):
    id : int
    content : str
    sender_id : int
    group_chat_id : int
    timestamp : datetime
    parent_message_id : Optional[int] = None

    class Config:
        from_attributes = True
   