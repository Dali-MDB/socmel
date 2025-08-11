from app.models.spaces import Space
from pydantic import BaseModel
from datetime import datetime

class SpaceBase(BaseModel):
    name : str

class SpaceCreate(SpaceBase):
    pass

class SpaceDisplay(SpaceBase):
    id : int
    owner_id : int
    members_nbr : int
    founded_on : datetime

class SpaceUpdate(SpaceBase):
    name: str|None = None


class Space(SpaceDisplay):
    class Config:
        from_attributes = True
