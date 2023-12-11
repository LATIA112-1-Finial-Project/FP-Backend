from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from flaskr.db import Base
from flaskr.models.Arxiv.id_name import ArxivIdName


class ArxivField(Base):
    __tablename__ = 'arxiv_field'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey('arxiv_id_name.id'))
    year: Mapped[int] = mapped_column(nullable=True)
    article_count: Mapped[int] = mapped_column(nullable=True)
    cross_list_count: Mapped[int] = mapped_column(nullable=True)
    total_article_count: Mapped[int] = mapped_column(nullable=True)
    field_name = relationship(ArxivIdName)

    def __init__(self, field_id=None, year=None, article_count=None, cross_list_count=None, total_article_count=None):
        self.field_id = field_id
        self.year = year
        self.article_count = article_count
        self.cross_list_count = cross_list_count
        self.total_article_count = total_article_count

    def __repr__(self):
        return f'<name={self.field_id!r})>'
