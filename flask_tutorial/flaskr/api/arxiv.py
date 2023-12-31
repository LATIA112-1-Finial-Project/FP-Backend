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
from flaskr.models.Arxiv.field import ArxivField
from flaskr.models.Arxiv.id_name import ArxivIdName
from flaskr.models.Arxiv.favorite_arxiv_list import Favorite

bp_arxiv = Blueprint('bp_arxiv', __name__, url_prefix='/api/v1/auth')

CORS(bp_arxiv, resources={r"/*": {"origins": "*"}})


@bp_arxiv.route('/arxiv_field/<int:field_id>', methods=['GET'])
@jwt_required()
def arxiv_field(field_id):
    # Get the id from the request body

    if field_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing id in request body'
        }), 400)
    if field_id < 1 or field_id > 20:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing id in request body'
        }), 400)

    id_to_query = field_id

    db = get_db()
    # Query the database to get the information
    # from 2023 to 1980, if the year cannot be found, break the loop
    arxiv_field_info_name_list = []
    arxiv_field_info_year_list = []
    arxiv_field_info_article_count_list = []
    arxiv_field_info_cross_list_count_list = []
    arxiv_field_info_total_article_count_list = []
    for year in range(2023, 1979, -1):
        arxiv_field_info = db.query(
            ArxivField.year,
            ArxivField.article_count,
            ArxivField.cross_list_count,
            ArxivField.total_article_count,
            ArxivIdName.name
        ).join(ArxivIdName, ArxivField.field_id == ArxivIdName.id).filter(ArxivField.field_id == id_to_query,
                                                                          ArxivField.year == year).first()
        if arxiv_field_info is None:
            break
        # store the arxiv_field_info in a list
        arxiv_field_info_name_list.append(arxiv_field_info.name)
        arxiv_field_info_year_list.append(arxiv_field_info.year)
        arxiv_field_info_article_count_list.append(arxiv_field_info.article_count)
        arxiv_field_info_cross_list_count_list.append(arxiv_field_info.cross_list_count)
        arxiv_field_info_total_article_count_list.append(arxiv_field_info.total_article_count)

    # Create a dictionary with the result

    response_data = jsonify({
        'code': 200,
        'msg': 'success',
        'data': {
            'name_list': arxiv_field_info_name_list,
            'year_list': arxiv_field_info_year_list,
            'article_count_list': arxiv_field_info_article_count_list,
            'cross_list_count_list': arxiv_field_info_cross_list_count_list,
            'total_article_count_list': arxiv_field_info_total_article_count_list
        }
    })

    return response_data, 200


@bp_arxiv.route('/arxiv_field/add_to_favorite', methods=['POST'])
@jwt_required()
def add_favorite_arxiv():
    # Get the id from the request body
    data = request.get_json()
    arxiv_id_list = data['arxiv_id_list']
    if arxiv_id_list is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing id in request body'
        }), 400)
    if not isinstance(arxiv_id_list, list):
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Wrong type'
        }), 400)
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
    user_id = user.id
    # get all arxiv id from favorite table
    favorite_arxiv_id_list = []
    for favorite in db.query(Favorite).filter(Favorite.user_id == user_id).all():
        favorite_arxiv_id_list.append(favorite.arxiv_id)
    # if arxiv id in favorite table, then pass
    # if arxiv id not in favorite table, then insert into favorite table
    # if favorite_arxiv_id_list not found arxiv id, then delete from favorite table
    for favorite_arxiv_id in favorite_arxiv_id_list:
        if favorite_arxiv_id not in arxiv_id_list:
            db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.arxiv_id == favorite_arxiv_id).delete()
            db.commit()
    for arxiv_id in arxiv_id_list:
        if arxiv_id not in favorite_arxiv_id_list:
            # check if arxiv id exist in arxiv table
            stmt = select(ArxivIdName).where(ArxivIdName.id == arxiv_id)
            is_arxiv = db.scalar(stmt)
            if is_arxiv is None:
                # skip
                continue
            favorite = Favorite(user_id=user_id, arxiv_id=arxiv_id)
            db.add(favorite)
            db.commit()
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': 'Add favorite arxiv successfully'
    }), 200)


@bp_arxiv.route('/arxiv_field/get_favorite_arxiv', methods=['GET'])
@jwt_required()
def get_favorite_arxiv():
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
    user_id = user.id
    # get all arxiv id from favorite table
    favorite_arxiv_id_list = []
    for favorite in db.query(Favorite).filter(Favorite.user_id == user_id).all():
        favorite_arxiv_id_list.append(favorite.arxiv_id)
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': favorite_arxiv_id_list
    }), 200)
