from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class ReputationScore(Base):
    __tablename__ = 'reputation_scores'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey('universities.id'))
    year: Mapped[int] = mapped_column(nullable=True)
    score: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, university_id=None, year=None, score=None):
        self.university_id = university_id
        self.year = year
        self.score = score

    def __repr__(self):
        return f'<User(id={self.id}, university_id={self.university_id}, year={self.year}, score={self.score})>'
