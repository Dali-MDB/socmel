from pydantic import BaseModel


class RoomBase(BaseModel):
    name : str

class RoomCreate(RoomBase):
    pass

class RoomDisplay(RoomBase):
    id : int
    space_id : int


class RoomUpdate(RoomBase):
    name : str | None = None

class Room(RoomDisplay):
    class Config:
        from_attributes = True
