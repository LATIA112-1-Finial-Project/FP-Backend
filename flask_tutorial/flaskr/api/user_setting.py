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
from flaskr.utils import send_email

bp_uni = Blueprint('bp_uni', __name__, url_prefix='/api/v1/auth')

CORS(bp_uni, resources={r"/*": {"origins": "*"}})


@bp_uni.route('/user_info', methods=('GET', 'POST'))
@jwt_required()
def user_info():
    if request.method == 'GET':
        email = get_jwt_identity()
        db = get_db()
        stmt = select(User).where(User.email == email)
        user = db.scalar(stmt)
        if user is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'Bad request'
            }), 400)
        response_data = jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'username': user.username,
                'email': user.email
            }
        })
        return response_data, 200
    return make_response(jsonify({
        'code': 400,
        'msg': 'error',
        'data': 'Bad request'
    }), 400)


# reset password api, if reset password successfully, then send email to notify user
@bp_uni.route('/reset_password', methods=['POST'])
@jwt_required()
def reset_password():
    data = request.get_json()
    email = get_jwt_identity()
    old_password = data['old_password']
    new_password = data['new_password']
    db = get_db()
    stmt = select(User).where(User.email == email)
    user = db.scalar(stmt)
    if user is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'User not found'
        }), 400)
    else:
        # reset password to new_password, new password is hashed by argon2
        if not Argon2().check_password_hash(user.password, old_password):
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'Old password is wrong'
            }), 400)
        else:
            try:
                u_new_password = Argon2().generate_password_hash(new_password)
                # change user password to new password
                user.password = u_new_password
                # commit to db
                db.commit()
                # send email to notify user
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
