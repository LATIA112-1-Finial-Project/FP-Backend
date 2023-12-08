# import sqlite3
import click
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import os

pjdir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(pjdir, '../instance/data.sqlite'))
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def get_db():
    session = db_session()
    return session


def close_db(e=None):
    db_session.close()


def init_db():
    """Clear the existing data and create new tables."""
    import flaskr.models.user
    import flaskr.models.post
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    """And then create users and posts."""
    import flaskr.models.user
    import flaskr.models.post
    """generate a user and a post"""
    from flaskr.models.user import User
    from flaskr.models.post import Post
    from flask_argon2 import Argon2
    from sqlalchemy import select
    db = get_db()
    u = User(username='admin7122', email='admin@latia.com', password=Argon2().generate_password_hash('admin'))
    db.add(u)
    db.commit()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
