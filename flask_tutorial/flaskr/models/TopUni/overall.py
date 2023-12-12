from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class Overall(Base):
    __tablename__ = 'overall'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey('university_id_name.id'))
    o_rank: Mapped[str] = mapped_column(nullable=True)
    o_score: Mapped[str] = mapped_column(nullable=True)
    o_year: Mapped[int] = mapped_column(nullable=True)

    def __init__(self, university_id=None, o_year=None, o_score=None, o_rank=None):
        self.university_id = university_id
        self.o_year = o_year
        self.o_score = o_score
        self.o_rank = o_rank

    def __repr__(self):
        return f'<User(id={self.id}, university_id={self.university_id})>'
