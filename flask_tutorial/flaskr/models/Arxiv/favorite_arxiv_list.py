from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey
from flaskr.db import Base
from flaskr.models.Arxiv.id_name import ArxivIdName


class Favorite(Base):
    __tablename__ = 'favorite_arxiv_list'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    arxiv_id: Mapped[int] = mapped_column(ForeignKey('arxiv_id_name.id'))
    arxiv = relationship(ArxivIdName)

    def __init__(self, user_id=None, arxiv_id=None):
        self.user_id = user_id
        self.arxiv_id = arxiv_id
