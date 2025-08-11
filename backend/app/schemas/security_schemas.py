from pydantic import BaseModel



class ChangeEmail(BaseModel):
    old_email : str 
    new_email : str
    key : str


class ChangePassword(BaseModel):
    email : str
    old_password : str
    new_password : str
    new_password_confirm : str
    key : str