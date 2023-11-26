import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response, jsonify
)

from flaskr.db import get_db
from flask_argon2 import Argon2
from flaskr.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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
            # username is already registered
            except IntegrityError as e:
                error = 'User {} is already registered.'.format(username)
            else:
                response = jsonify({'message': 'User created successfully.'})
                response.status_code = 201
                return response

        flash(error)

    return jsonify({'message': 'Register failed.'}), 401


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        stmt = select(User).where(User.username == username)
        print(stmt)
        user = db.scalar(stmt)
        print(user.username)
        if user is None:
            error = 'Incorrect username.'
        elif not Argon2().check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            access_token = create_access_token(identity=username)
            return jsonify(access_token="Bearer " + access_token)

        flash(error)

    return jsonify({'message': 'Login failed.'}), 401


@bp.route('/protected', methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        stmt = select(User).where(User.id == user_id)
        g.user = db.scalar(stmt)


@bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logout successfully, GoodBye!'}), 200


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'error': 'Authentication required'}), 401

        return view(**kwargs)

    return wrapped_view
