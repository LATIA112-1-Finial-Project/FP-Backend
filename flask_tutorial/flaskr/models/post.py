import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flaskr.db import Base
from flaskr.models.user import User


class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    title = Column(String(50), nullable=True)
    body = Column(String(120), nullable=True)
    user = relationship(User)

    def __init__(self, author_id=None, title=None, created=None, body=None):
        self.author_id = author_id
        self.created = created
        self.title = title
        self.body = body


    def __repr__(self):
        return f'<Title {self.title!r}>'
