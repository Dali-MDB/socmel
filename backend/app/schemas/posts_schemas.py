from app.models.posts import Post
from app.schemas.post_attachments_schema import PostAttachmentDisplay
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    title : str
    content : str


class PostCreate(PostBase):
    pass


class PostDisplay(PostBase):
    id : int
    created_at : datetime
    likes_nbr : int
    user_id : int
    space_id : int | None 
    attachments : list[PostAttachmentDisplay] | None
    


class PostUpdate(PostBase):
    title : str | None = None
    content : str | None = None


class Post(PostDisplay):
    class Config:
        from_attributes = True


