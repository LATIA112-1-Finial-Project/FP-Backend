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

bp_uni = Blueprint('bp_uni', __name__, url_prefix='/auth')


@bp_uni.route('/user_infor', methods=('GET', 'POST'))
@jwt_required()
def user_infor():
    if request.method == 'GET':
        username = get_jwt_identity()
        db = get_db()
        stmt = select(User).where(User.username == username)
        user = db.scalar(stmt)
        return jsonify({'username': 'Hi, ' + user.username})
    return jsonify({'message': 'User information failed.'}), 401
