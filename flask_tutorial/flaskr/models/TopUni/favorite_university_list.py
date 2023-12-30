from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey
from flaskr.db import Base
from flaskr.models.TopUni.university_id_name import University


class Favorite(Base):
    __tablename__ = 'favorite_university_list'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    university_id: Mapped[int] = mapped_column(ForeignKey('university_id_name.id'))
    university = relationship(University)

    def __init__(self, user_id=None, university_id=None):
        self.user_id = user_id
        self.university_id = university_id
