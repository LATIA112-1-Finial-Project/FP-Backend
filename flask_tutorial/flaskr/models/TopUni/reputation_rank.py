from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from flaskr.db import Base


class ReputationRank(Base):
    __tablename__ = 'reputation_ranks'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey('universities.id'))
    year: Mapped[int] = mapped_column(nullable=True)
    rank: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, university_id=None, year=None, rank=None):
        self.university_id = university_id
        self.year = year
        self.rank = rank

    def __repr__(self):
        return f'<User(id={self.id}, university_id={self.university_id}, year={self.year}, rank={self.rank})>'
