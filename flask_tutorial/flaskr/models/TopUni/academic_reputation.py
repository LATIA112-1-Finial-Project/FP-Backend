from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class Academic(Base):
    __tablename__ = 'academic_reputation'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey('university_id_name.id'))
    ar_rank: Mapped[str] = mapped_column(nullable=True)
    ar_score: Mapped[str] = mapped_column(nullable=True)
    ar_year: Mapped[int] = mapped_column(nullable=True)

    def __init__(self, university_id=None, ar_year=None, ar_score=None, ar_rank=None):
        self.university_id = university_id
        self.ar_year = ar_year
        self.ar_score = ar_score
        self.ar_rank = ar_rank

    def __repr__(self):
        return f'<User(id={self.id}, university_id={self.university_id})>'
