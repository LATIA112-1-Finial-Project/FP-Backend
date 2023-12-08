import os
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import DateTime, Boolean
import datetime
from flaskr.db import Base
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired, BadSignature
from flask import current_app


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    is_confirmed: Mapped[bool] = mapped_column(nullable=False, default=False)
    confirmed_on: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, username=None, email=None, password=None, is_confirmed=False, confirmed_on=None):
        self.username = username
        self.email = email
        self.password = password
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on

    def __repr__(self):
        return f'<username={self.username!r})>'

    @staticmethod
    def generate_token(email):
        config_secret_key = os.environ.get('SECRET_KEY')
        config_salt = os.environ.get('SECURITY_PASSWORD_SALT')
        s = URLSafeTimedSerializer(config_secret_key)
        return s.dumps(email, salt=config_salt)

    @staticmethod
    def confirm_token(token, expiration=3600):
        config_secret_key = os.environ.get('SECRET_KEY')
        config_salt = os.environ.get('SECURITY_PASSWORD_SALT')
        serializer = URLSafeTimedSerializer(config_secret_key)
        # noinspection PyBroadException
        try:
            email = serializer.loads(
                token, salt=config_salt, max_age=expiration
            )
            return email
        except Exception as e:
            return e
