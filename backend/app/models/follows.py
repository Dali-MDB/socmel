from app.database import Base
from sqlalchemy import Column,Integer,ForeignKey,UniqueConstraint,Boolean
from sqlalchemy.orm import relationship


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer,primary_key=True,index=True)
    follower_id = Column(Integer,ForeignKey('users.id'))
    followed_id = Column(Integer,ForeignKey('users.id'))
    is_pending = Column(Boolean,default=True)

    follower = relationship("User",back_populates="following",foreign_keys=[follower_id])
    followed = relationship("User",back_populates="followers",foreign_keys=[followed_id])

    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
    )

    def __repr__(self):
        return f'follow: {self.follower_id} to {self.followed_id}'
    

class FollowRequest(Base):
    __tablename__ = "follow_requests"

    id = Column(Integer,primary_key=True,index=True)
    from_user_id = Column(Integer,ForeignKey('users.id'))
    to_user_id = Column(Integer,ForeignKey('users.id'))

    from_user = relationship("User",back_populates="follow_requests_sent",foreign_keys=[from_user_id])
    to_user = relationship("User",back_populates="follow_requests_received",foreign_keys=[to_user_id])

    __table_args__ = (
        UniqueConstraint('from_user_id', 'to_user_id', name='unique_follow'),
    )



    
