from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class Employer(Base):
    __tablename__ = 'employer_reputation'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey('university_id_name.id'))
    er_rank: Mapped[str] = mapped_column(nullable=True)
    er_score: Mapped[str] = mapped_column(nullable=True)
    er_year: Mapped[int] = mapped_column(nullable=True)

    def __init__(self, university_id=None, er_year=None, er_score=None, er_rank=None):
        self.university_id = university_id
        self.er_year = er_year
        self.er_score = er_score
        self.er_rank = er_rank

    def __repr__(self):
        return f'<User(id={self.id}, university_id={self.university_id})>'
