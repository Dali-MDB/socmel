from app.database import Base 
from sqlalchemy import Column,Integer,text,DateTime,ForeignKey,Table,String,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime



class DmMessage(Base):
    __tablename__ = "dm_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(512))
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.now())
    is_read = Column(Boolean, default=False)
    parent_message_id = Column(Integer,ForeignKey("dm_messages.id"),nullable=True)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="messages_received")
    parent_message = relationship("DmMessage",remote_side=[id],back_populates="replies")
    replies = relationship("DmMessage",back_populates='parent_message')


    def __repr__(self):
        return f'dm: ({self.sender}) -> ({self.recipient})'
    



class RoomMessage(Base):
    __tablename__ = "room_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(512))
    sender_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    timestamp = Column(DateTime, default=datetime.now())
    parent_message_id = Column(Integer,ForeignKey("room_messages.id"),nullable=True)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="room_messages_sent")
    parent_message = relationship("RoomMessage",remote_side=[id],back_populates="replies")
    replies = relationship("RoomMessage",back_populates='parent_message')
    room = relationship("Room", foreign_keys=[room_id], back_populates="messages")


    def __repr__(self):
        return f'dm: ({self.sender}) -> ({self.recipient})'
