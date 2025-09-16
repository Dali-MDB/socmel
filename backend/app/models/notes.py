from app.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from datetime import datetime



class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer,primary_key=True,index=True)
    content = Column(String(255))
    user_id = Column(Integer,ForeignKey("users.id"),nullable=True,unique=True)
    created_at = Column(DateTime,default=datetime.now())

    user = relationship("User",back_populates="note")