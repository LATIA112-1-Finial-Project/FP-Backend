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
    import flaskr.models.Arxiv.field
    import flaskr.models.Arxiv.id_name
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
    u = User(username='admin', email='admin@latia.com',
             password=Argon2().generate_password_hash('admin'),
             is_confirmed=True, confirmed_on='2021-01-01 00:00:00')
    db.add(u)
    db.commit()

    import flaskr.models.Arxiv.field
    import flaskr.models.Arxiv.id_name
    """
    push data into db from flask_tutorial/generate_table/Arxiv/arxiv_id_name.csv
    push data into db from flask_tutorial/generate_table/Arxiv/arxiv_field.csv
    """
    from flaskr.models.Arxiv.id_name import ArxivIdName
    from flaskr.models.Arxiv.field import ArxivField
    import csv
    first_time = True
    with open(os.path.join(pjdir, 'generate_table/Arxiv/arxiv_id_name.csv'), 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if first_time:
                first_time = False
                continue
            db = get_db()
            u_a_id_name = ArxivIdName(name=row[1])
            db.add(u_a_id_name)
            db.commit()
    first_time = True
    with open(os.path.join(pjdir, 'generate_table/Arxiv/arxiv_field.csv'), 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if first_time:
                first_time = False
                continue
            db = get_db()
            u_a_f = ArxivField(field_id=row[0], year=row[1], article_count=row[2],
                               cross_list_count=row[3], total_article_count=row[4])
            db.add(u_a_f)
            db.commit()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
