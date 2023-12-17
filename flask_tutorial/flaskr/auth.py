import functools
import datetime
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
from flask_mail import Mail, Message
from flaskr.utils import send_email
from flask import current_app

bp = Blueprint('auth', __name__, url_prefix='/api/v1')

CORS(bp, resources={r"/*": {"origins": "*"}})


@bp.route("/confirm_email", methods=["POST"])
def confirm_email():

    token = request.headers['Authorization']
    email = User.confirm_token(token)

    if email == "error: SignatureExpired('token expired')":
        return jsonify({
            'code': 400,
            'msg': 'expired',
            'data': 'token expired'
        }), 400
    else:
        data = request.get_json()
        username = data['username']
        password = data['password']
        chk_password = data['chk_password']
        if password == '' or chk_password == '':
            return jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'Required missing'
            }), 400
        if password != chk_password:
            return jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'Not the same'
            }), 400
        if username == '':
            return jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'Required missing'
            }), 400
        # add user to db
        db = get_db()
        # check if username or email is already registered
        stmt = select(User).where(User.email == email)
        user = db.scalar(stmt)
        if user is not None:
            return jsonify({
                'code': 400,
                'msg': 'duplicate',
                'data': 'Register failed'
            }), 400
        stmt = select(User).where(User.username == username)
        user = db.scalar(stmt)
        if user is not None:
            return jsonify({
                'code': 400,
                'msg': 'duplicate',
                'data': 'Register failed'
            }), 400

        u = User(username=username, email=email, password=Argon2().generate_password_hash(password),
                 is_confirmed=True, confirmed_on=datetime.datetime.now())
        try:
            db.add(u)
            db.commit()
        except IntegrityError as e:
            return jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'Register failed'
            }), 400
        response_data = jsonify({
            'code': 201,
            'msg': 'success',
            'data': ''
        })
        return response_data, 201


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']

    if email == '':
        return jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Required missing'
        }), 400

    db = get_db()
    error = None

    if error is None:
        # search db to check if email is already registered
        stmt = select(User).where(User.email == email)
        user = db.scalar(stmt)
        # if email is registered, return error
        if user is not None:
            return jsonify({
                'code': 200,
                'msg': 'duplicate',
                'data': 'Register failed'
            }), 200
        # if email is not registered, create token and send email to user
        u = User(email=email)
        token = u.generate_token(u.email)
        register_confirm_url = current_app.config['FRONTEND_URL'] + '/register/verify?token=' + token
        html = render_template("accounts/confirm_email.html", confirm_url=register_confirm_url)
        subject = "LATIAFP - Please confirm your email"
        send_email(u.email, subject, html)
        response_data = jsonify({
            'code': 201,
            'msg': 'success',
            'data': ''
        })
        return response_data, 201
    if error is not None:
        return jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Required missing'
        }), 400


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    db = get_db()
    stmt = select(User).where(User.email == email)
    user = db.scalar(stmt)
    if user is None:
        return jsonify({
            'code': 401,
            'msg': 'error',
            'data': {
                'token': '',
                'type': '',
                'detail': 'Login failed, please check your email and password, or check the account exist or not.'
            }
        }), 401
    elif not Argon2().check_password_hash(user.password, password):
        return jsonify({
            'code': 401,
            'msg': 'error',
            'data': {
                'token': '',
                'type': '',
                'detail': 'Login failed, please check your email and password, or check the account exist or not.'
            }
        }), 401
    if user.is_confirmed is False:
        return jsonify({
            'code': 401,
            'msg': 'not_confirmed',
            'data': {
                'token': '',
                'type': '',
                'detail': 'Please confirm your account.'
            }
        }), 401
    session.clear()
    session['user_id'] = user.id
    access_token = create_access_token(identity=email)
    response_data = jsonify({
        'code': 200,
        'msg': 'success',
        'data': {
            'token': access_token,
            'type': 'Bearer',
            'detail': 'Login successfully, Welcome!'
        }
    })
    return response_data, 200


# forget password api, send token link to user's email,
# direct to reset password page (FRONTEND_URL + ?token=token), token will expire in 10 minutes
# and reset password
@bp.route('/forget_password', methods=['POST'])
def forget_password():
    data = request.get_json()
    email = data['email']
    db = get_db()
    stmt = select(User).where(User.email == email)
    user = db.scalar(stmt)
    if user is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Email not found'
        }), 400)
    else:
        token = user.generate_token(user.email)
        forget_password_url = current_app.config['FRONTEND_URL'] + '/resetPassword?token=' + token
        html = render_template("accounts/forget_password.html", username=user.username, confirm_url=forget_password_url)
        send_email(user.email, "忘記密碼確認信", html)
        return make_response(jsonify({
            'code': 200,
            'msg': 'success',
            'data': 'Send forget password successfully, please check your email'
        }), 200)


# confirm token and reset password (forget password confirm api)
@bp.route('/forget_password_confirm', methods=['POST'])
def forget_password_confirm():
    data = request.get_json()
    token = request.headers['Authorization']
    password = data['password']
    chk_password = data['chk_password']
    if password == '' or chk_password == '':
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Required missing'
        }), 400)
    if password != chk_password:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Not the same'
        }), 400)
    email = User.confirm_token(token)
    if email == "error: SignatureExpired('token expired')":
        return jsonify({
            'code': 400,
            'msg': 'expired',
            'data': 'token expired'
        }), 400
    else:
        db = get_db()
        stmt = select(User).where(User.email == email)
        user = db.scalar(stmt)
        if Argon2().check_password_hash(user.password, password):
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'New same as old'
            }), 400)
        if user is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'User not found'
            }), 400)
        else:
            try:
                user.password = Argon2().generate_password_hash(password)
                # commit to db
                db.commit()
                html = render_template("accounts/reset_password.html", username=user.username)
                send_email(user.email, "密碼重設成功通知", html)
            except IntegrityError as e:
                return make_response(jsonify({
                    'code': 400,
                    'msg': 'error',
                    'data': 'Reset password failed'
                }), 400)
            else:
                return make_response(jsonify({
                    'code': 200,
                    'msg': 'success',
                    'data': 'Reset password successfully, please check your email'
                }), 200)


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
    response_data = jsonify({
        'code': 200,
        'msg': 'success',
        'data': 'Logout successfully, GoodBye!'
    })
    return response_data, 200


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            response_data = jsonify({
                'code': 401,
                'msg': 'error',
                'data': 'Authentication required!'
            })
            return response_data, 401

        return view(**kwargs)

    return wrapped_view
