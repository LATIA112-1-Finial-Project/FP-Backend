from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class University(Base):
    __tablename__ = 'universities'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f'<User(id={self.id}, name={self.name})>'
