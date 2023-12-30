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
from flaskr.models.post import Post, PostLike
from flaskr.models.boards import Boards
import datetime

bp_posts = Blueprint('bp_posts', __name__, url_prefix='/api/v1/auth')

CORS(bp_posts, resources={r"/*": {"origins": "*"}})


@bp_posts.route('/posts', methods=['POST'])
@jwt_required()
def new_posts():
    # add a post
    title = request.json.get('title')
    body = request.json.get('body')
    board_id = int(request.json.get('board_id'))
    # board_id = 1  -> arxiv, 2 -> top universities
    if title is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing title in request body'
        }), 400)
    if body is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing body in request body'
        }), 400)
    if board_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing board_id in request body'
        }), 400)
    if board_id < 1 or board_id > 2:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'board_id not exist'
        }), 400)
    db = get_db()
    user_email = get_jwt_identity()
    # get user_id
    stmt = select(User).where(User.email == user_email)
    user = db.scalar(stmt)
    user_id = user.id
    post = Post(author_id=user_id, board_id=board_id,
                created=datetime.datetime.utcnow(), title=title, body=body, likes=0)
    db.add(post)
    db.commit()
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': 'post added'
    }), 200)


@bp_posts.route('/posts/<int:board_id>/<int:post_id>', methods=['GET'])
@jwt_required()
def get_posts(board_id, post_id):
    # get all posts
    if board_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing board_id in request body'
        }), 400)
    if board_id < 1 or board_id > 2:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'board_id not exist'
        }), 400)
    if post_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing post_id in request body'
        }), 400)
    db = get_db()

    post_info = db.query(Post.id, Post.title, Post.body, Post.created, Post.author_id, Boards.board_name,
                         Post.likes).join(Boards, Post.board_id == Boards.id).filter(Post.id == post_id,
                                                                                     Boards.id == board_id).first()

    if post_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'post not exist'
        }), 400)

    # get user name from post_info.author
    author_name = db.query(User.username).filter(User.id == post_info.author_id).first()

    print("This is post info", post_info)
    if post_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'post not exist'
        }), 400)

    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': {
            'title': post_info.title,
            'body': post_info.body,
            'created': post_info.created,
            'username': author_name.username,
            'board_name': post_info.board_name,
            'likes': post_info.likes
        }
    }), 200)


@bp_posts.route('/like_post', methods=['POST'])
@jwt_required()
def like_post():
    board_id = int(request.json.get('board_id'))
    post_id = int(request.json.get('post_id'))
    # get all posts
    if board_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing board_id in request body'
        }), 400)
    if board_id < 1 or board_id > 2:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'board_id not exist'
        }), 400)
    if post_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing post_id in request body'
        }), 400)
    db = get_db()
    # consider the case that the user has already liked the post, if so, delete the like
    # check if the user has already liked the post
    user_email = get_jwt_identity()
    # get user_id
    stmt = select(User).where(User.email == user_email)
    user = db.scalar(stmt)
    user_id = user.id
    post_like_info = db.query(PostLike).filter(PostLike.user_id == user_id, PostLike.post_id == post_id,
                                               PostLike.board_id == board_id).first()
    if post_like_info is None:
        # the user has not liked the post, add a like
        post_like = PostLike(user_id=user_id, post_id=post_id, board_id=board_id, created=datetime.datetime.utcnow())
        if post_like is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'post not exist'
            }), 400)
        db.add(post_like)
        db.commit()
        # update the likes in post table
        post_info = db.query(Post).filter(Post.id == post_id, Post.board_id == board_id).first()
        if post_info is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'post not exist'
            }), 400)
        post_info.likes = post_info.likes + 1
        db.commit()
        return make_response(jsonify({
            'code': 200,
            'msg': 'success',
            'data': 'post liked'
        }), 200)
    else:
        # the user has liked the post, delete the like
        db.delete(post_like_info)
        db.commit()
        # update the likes in post table
        post_info = db.query(Post).filter(Post.id == post_id).first()
        if post_info is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'post not exist'
            }), 400)
        post_info.likes = post_info.likes - 1
        db.commit()
        return make_response(jsonify({
            'code': 200,
            'msg': 'success',
            'data': 'post unliked'
        }), 200)


@bp_posts.route('/like_post/<int:board_id>/<int:post_id>', methods=['GET'])
@jwt_required()
def get_like_post(board_id, post_id):
    # get all posts
    if board_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing board_id in request'
        }), 400)
    if board_id < 1 or board_id > 2:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'board_id not exist'
        }), 400)
    if post_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing post_id in request'
        }), 400)
    db = get_db()
    # get the number of likes
    post_info = db.query(Post.likes).filter(Post.id == post_id, Post.board_id == board_id).first()
    if post_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'post not exist'
        }), 400)
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': post_info.likes
    }), 200)
