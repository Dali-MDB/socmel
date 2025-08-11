from pydantic import BaseModel
from datetime import datetime


class InvitationBase(BaseModel):
    max_uses:int
    expires_at:datetime

class InvitationCreate(InvitationBase):
    pass


class InvitationDisplay(InvitationBase):
    id:int
    token:str
