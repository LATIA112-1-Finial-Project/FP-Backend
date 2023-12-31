from sqlalchemy.orm import mapped_column, Mapped
from flaskr.db import Base


class Boards(Base):
    __tablename__ = 'boards'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    board_name: Mapped[str] = mapped_column(unique=True, nullable=True)

    def __init__(self, board_name=None):
        self.board_name = board_name

    def __repr__(self):
        return f'<Board {self.board_name!r}>'
