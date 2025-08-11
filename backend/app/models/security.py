from app.database import Base 
from sqlalchemy import Column,Integer,text,DateTime,ForeignKey,Table,String,Boolean,Enum
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from enum import Enum as PyEnum

class verification_code_purpose(str,PyEnum):
    CHANGE_EMAIL = "CHANGE_EMAIL"
    CHANGE_PASSWORD = "CHANGE_PASSWORD"
    RESET_PASSWORD = "RESET_PASSWORD"


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String(50),unique=True,index=True)
    code = Column(String(8))
    purpose = Column(Enum(verification_code_purpose))
    created_at = Column(DateTime, default=datetime.now())
    expires_at =Column(DateTime)
    is_used = Column(Boolean,default=False)
