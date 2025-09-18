from sqlalchemy import Column, Integer, String, ForeignKey,Text,DateTime,Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    likes_nbr = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    space_id = Column(Integer,ForeignKey('spaces.id'),nullable=True)
    for_space = Column(Boolean,default=False)
    tags = Column(Text,nullable=True)    #tags separated by commas

    user = relationship("User", back_populates="posts")
    likes = relationship("Like",back_populates='post')
    comments = relationship("Comment",back_populates='post')
    space = relationship("Space",back_populates="posts")
    attachments = relationship("PostAttachment",back_populates='post',cascade="all,delete")   #delete when deleting post


    def __repr__(self):
        return f'post: {self.title} by {self.user.email} - {self.created_at}'
    

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

    def __repr__(self):
        return f'like on {self.post_id} by {self.user.email}'
    


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer,primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer,ForeignKey('users.id'))
    post_id = Column(Integer,ForeignKey('posts.id'))
    likes_nbr = Column(Integer,default=0)
    parent_id = Column(Integer,ForeignKey('comments.id'),nullable=True)

    user = relationship("User",back_populates='comments')
    post = relationship("Post",back_populates='comments')
    parent_comment = relationship("Comment",remote_side = [id],back_populates='sub_comments')
    sub_comments = relationship("Comment",back_populates='parent_comment')
    reactions = relationship("Reaction",back_populates="comment",cascade="all,delete")   #delete when deleting comment




class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer,primary_key=True, index=True)
    reaction_type = Column(String(20))
    user_id = Column(Integer,ForeignKey("users.id"))
    comment_id = Column(Integer,ForeignKey("comments.id"))

    user = relationship("User",back_populates="reactions")
    comment = relationship("Comment",back_populates="reactions",cascade="all,delete")   #delete when deleting comment



class PostAttachment(Base):
    __tablename__ = "post_attachments"

    id = Column(Integer,primary_key=True, index=True)
    file = Column(Text,nullable=False)
    file_public_id = Column(Text,nullable=False)
    post_id = Column(Integer,ForeignKey('posts.id'))

    post = relationship(Post,back_populates='attachments')

    



