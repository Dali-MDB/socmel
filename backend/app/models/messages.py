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
    attachment = Column(String(255),nullable=True)
    attachment_public_id = Column(String(255),nullable=True)
    
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
    attachment = Column(String(255),nullable=True)
    attachment_public_id = Column(String(255),nullable=True)
    sender = relationship("User", foreign_keys=[sender_id], back_populates="room_messages_sent")
    parent_message = relationship("RoomMessage",remote_side=[id],back_populates="replies")
    replies = relationship("RoomMessage",back_populates='parent_message')
    room = relationship("Room", foreign_keys=[room_id], back_populates="messages")

    @property
    def space_id(self):
        return self.room.space_id
    def __repr__(self):
        return f'dm: ({self.sender}) -> ({self.recipient})'
#association table for group chat

group_chat_members = Table('group_chat_members',Base.metadata,
    Column('group_chat_id',Integer,ForeignKey('group_chat.id'),primary_key=True),
    Column('user_id',Integer,ForeignKey('users.id'),primary_key=True)
)





class GroupChat(Base):
    __tablename__ = 'group_chat'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50),index=True)
    owner_id = Column(Integer,ForeignKey('users.id'))
    created_at = Column(DateTime,default=datetime.now())

    owner = relationship("User",back_populates="owned_group_chats")
    members = relationship("User",secondary=group_chat_members,back_populates="group_chats")
    messages = relationship("GroupChatMessage",back_populates="group_chat")

    @property
    def members_ids(self):
        return [member.id for member in self.members]
    

class GroupChatMessage(Base):
    __tablename__ = "group_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(512))
    sender_id = Column(Integer,ForeignKey('users.id'))
    group_chat_id = Column(Integer,ForeignKey('group_chat.id'))
    timestamp = Column(DateTime,default=datetime.now())
    parent_message_id = Column(Integer,ForeignKey("group_chat_messages.id"),nullable=True)
    attachment = Column(String(255),nullable=True)
    attachment_public_id = Column(String(255),nullable=True)
    sender = relationship("User",foreign_keys=[sender_id],back_populates="group_chat_messages_sent")
    group_chat = relationship("GroupChat",back_populates="messages")
    parent_message = relationship("GroupChatMessage",remote_side=[id],back_populates="replies")
    replies = relationship("GroupChatMessage",back_populates='parent_message')



