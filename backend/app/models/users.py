from fastapi import Depends
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.follows import Follow,FollowRequest
from app.models.messages import DmMessage, RoomMessage,group_chat_members


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True) 
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

    posts = relationship("Post",back_populates='user')
    likes = relationship("Like",back_populates='user')
    comments = relationship("Comment",back_populates='user')
    owned_spaces = relationship("Space",back_populates='owner')
    spaces = relationship("Space",secondary="membership",back_populates='members')
    followers = relationship("Follow", back_populates="followed",foreign_keys=[Follow.followed_id])
    following = relationship("Follow", back_populates="follower",foreign_keys=[Follow.follower_id])

    follow_requests_sent = relationship("FollowRequest", back_populates="from_user",foreign_keys=[FollowRequest.from_user_id])
    follow_requests_received = relationship("FollowRequest", back_populates="to_user",foreign_keys=[FollowRequest.to_user_id])

    messages_sent = relationship(
        "DmMessage",
        back_populates="sender",
        foreign_keys="[DmMessage.sender_id]"
    )
    messages_received = relationship(
        "DmMessage",
        back_populates="recipient",
        foreign_keys="[DmMessage.recipient_id]"
    )
    room_messages_sent = relationship(
        "RoomMessage",
        back_populates="sender",
        foreign_keys="[RoomMessage.sender_id]"
    )

    reactions = relationship("Reaction",back_populates="user")
    group_chats = relationship("GroupChat",secondary=group_chat_members,back_populates="members")
    owned_group_chats = relationship("GroupChat",back_populates="owner")
    group_chat_messages_sent = relationship("GroupChatMessage",back_populates="sender",foreign_keys="[GroupChatMessage.sender_id]")

    def __repr__(self):
        return f'user: {self.email}'


