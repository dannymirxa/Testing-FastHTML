from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__  = 'User'

    Id = Column(Integer, primary_key = True, index = True)
    Email = Column(String, index = True)
    Password = Column(String, index = True)
    Name = Column(String, index = True)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
class Post(Base):
    __tablename__  = 'Post'

    Id = Column(Integer, primary_key = True, index = True)
    User_Id = Column(Integer, ForeignKey('User.Id'), index = True)
    Image = Column(String, index = True)
    Caption = Column(String, index = True)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'Comment'

    Id = Column(Integer, primary_key=True, index=True)
    User_Id = Column(Integer, ForeignKey('User.Id'), nullable=False)
    Post_Id = Column(Integer, ForeignKey('Post.Id'), nullable=False)
    Text = Column(String(255))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
