from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User(id={self.id}, username={self.username!r}, password={self.password!r})>'
