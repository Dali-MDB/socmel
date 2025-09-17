from pydantic import BaseModel



class PostAttachmentDisplay(BaseModel):
    id : int
    file : str
    file_public_id : str
    post_id : int

    class Config:
        from_attributes = True