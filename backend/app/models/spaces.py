from app.database import Base
from sqlalchemy import Column,Integer,String,Text,ForeignKey,DateTime,Table
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.models.users import User

class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(50),index=True)
    owner_id = Column(Integer,ForeignKey('users.id'))
    members_nbr = Column(Integer,default=1)
    founded_on = Column(DateTime,default=datetime.now())

    owner = relationship("User",back_populates='owned_spaces')
    rooms = relationship("Room",back_populates='space')
    posts = relationship("Post",back_populates='space')
    invitations = relationship("SpaceInvitation",back_populates='space')
    members = relationship("User",secondary="membership",back_populates='spaces')

    def add_member(self,user:User):
        self.members.append(user)
        self.members_nbr += 1

    def remove_member(self,user:User):
        self.members.remove(user)
        self.members_nbr -= 1

    @property
    def members_ids(self):
        return [m.id for m in self.members]

    def __repr__(self):
        return f'space: {self.name} - {self.founded_on}'
    

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(50),index=True)
    space_id = Column(Integer,ForeignKey('spaces.id'))

    space = relationship("Space",back_populates='rooms')
    messages = relationship("RoomMessage", back_populates="room")


    __table_args__ = (
        UniqueConstraint('name','space_id',name='uniq-room-space'),
    )


class SpaceInvitation(Base):
    __tablename__ = "space_invitations"

    id = Column(Integer,primary_key=True,index=True)
    token = Column(String(64),unique=True)
    created_at = Column(DateTime,default=datetime.now())
    expires_at = Column(DateTime)
    max_uses = Column(Integer,default=1)
    current_uses = Column(Integer,default=0)
    space_id = Column(Integer,ForeignKey('spaces.id'))
    space = relationship("Space",back_populates='invitations')

    def __repr__(self):
        return f'invitation: {self.token} - {self.created_at}'
    
    

#association table for the many to many relationship between users and spaces
membership = Table(
    'membership',
    Base.metadata,
    Column('user_id',Integer,ForeignKey('users.id')),
    Column('space_id',Integer,ForeignKey('spaces.id')),

)
