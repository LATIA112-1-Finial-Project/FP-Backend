import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from flaskr.db import Base
from flaskr.models.user import User
from flaskr.models.boards import Boards


class PostLike(Base):
    __tablename__ = 'post_likes'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # one to one, one user can only like in one post
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'))
    created: Mapped[str] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id=None, post_id=None, board_id=None, created=None):
        self.user_id = user_id
        self.post_id = post_id
        self.board_id = board_id
        self.created = created


class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'))
    created: Mapped[str] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    title: Mapped[str] = mapped_column(String(80), nullable=False)
    body: Mapped[str] = mapped_column(String(1000), nullable=False)
    likes: Mapped[int] = mapped_column(default=0)
    author = relationship(User)
    board = relationship(Boards)
    post_like = relationship(PostLike)

    def __init__(self, author_id=None, board_id=None, post_like_id=None, title=None, created=None, body=None,
                 likes=None):
        self.author_id = author_id
        self.board_id = board_id
        self.post_like_id = post_like_id
        self.created = created
        self.title = title
        self.body = body
        self.likes = likes

    def __repr__(self):
        return f'<Title {self.title!r}>'


class CommentLike(Base):
    __tablename__ = 'comment_likes'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created: Mapped[str] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id=None, created=None):
        self.user_id = user_id
        self.created = created


class Comment(Base):
    __tablename__ = 'comments'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
    comment_like_id: Mapped[int] = mapped_column(ForeignKey('comment_likes.id'))
    created: Mapped[str] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    body: Mapped[str] = mapped_column(String(1000), nullable=False)
    likes: Mapped[int] = mapped_column(default=0)
    author = relationship(User)
    post = relationship(Post)
    comment_like = relationship(CommentLike)

    def __init__(self, author_id=None, post_id=None, comment_like_id=None, created=None, body=None, likes=None):
        self.author_id = author_id
        self.post_id = post_id
        self.comment_like_id = comment_like_id
        self.created = created
        self.body = body
        self.likes = likes

    def __repr__(self):
        return f'<Comment {self.body!r}>'
