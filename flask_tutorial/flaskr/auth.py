import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db
from flask_argon2 import Argon2
from flaskr.models.user import User
from sqlalchemy import select

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                u = User(username=username, password=Argon2().generate_password_hash(password))
                db.add(u)
                db.commit()
                # db.execute(
                #     "INSERT INTO user (username, password) VALUES (?, ?)",
                #     (username, Argon2().generate_password_hash(password)),
                # )
                # db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        stmt = select(User).where(User.username == username)
        user = db.scalar(stmt)
        if user is None:
            error = 'Incorrect username.'
        elif not Argon2().check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('hello'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        stmt = select(User).where(User.id == user_id)
        g.user = db.scalar(stmt)
        # g.user = get_db().execute(
        #     'SELECT * FROM user WHERE id = ?', (user_id,)
        # ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view