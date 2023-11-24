from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from .engine import Base

__all__ = ['User']


class User(Base):
    __tablename__ = 'Users'
    _id = Column(Integer, primary_key=True)
    email = Column(String(100))
    hashed_password = Column(String(100))
