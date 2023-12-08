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
from flask_cors import CORS, cross_origin

bp = Blueprint('auth', __name__, url_prefix='/api/v1')

CORS(bp, resources={r"/*": {"origins": "*"}})


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not email:
        error = 'Email is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        try:
            u = User(username=username, email=email, password=Argon2().generate_password_hash(password))
            db.add(u)
            db.commit()
        # email is already registered
        except IntegrityError as e:
            return jsonify({
                'code': 200,
                'msg': 'duplicate',
                'data': 'Register failed'
            }), 200
        else:
            response_data = jsonify({
                'code': 201,
                'msg': 'success',
                'data': ''
            })
            return response_data, 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    db = get_db()
    error = None
    stmt = select(User).where(User.email == email)
    user = db.scalar(stmt)
    if user is None:
        error = 'Incorrect email.'
    elif not Argon2().check_password_hash(user.password, password):
        error = 'Incorrect password.'
    if error is None:
        session.clear()
        session['user_id'] = user.id
        access_token = create_access_token(identity=email)
        response_data = jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'token': access_token,
                'type': 'Bearer'
            }
        })
        return response_data, 200
    return jsonify({
        'code': 401,
        'msg': 'error',
        'data': 'Login failed'
    }), 401


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
