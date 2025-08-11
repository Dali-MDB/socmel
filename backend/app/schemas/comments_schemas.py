from pydantic import BaseModel
from typing import List


class CommentDisplay(BaseModel):
    id : int
    content : str
    user_id : int
    post_id : int
    likes_nbr : int
    parent_id : int | None
    sub_comments : List["CommentDisplay"] = []
    class Config:
        from_attributes = True