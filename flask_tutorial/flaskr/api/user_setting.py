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