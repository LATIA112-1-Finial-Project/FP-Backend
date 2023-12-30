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
from flaskr.models.post import Post, PostLike, Comment, CommentLike
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
        # update the likes in post table
        post_info = db.query(Post).filter(Post.id == post_id, Post.board_id == board_id).first()
        if post_info is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'post not exist'
            }), 400)
        db.add(post_like)
        db.commit()
        post_info.likes = post_info.likes + 1
        db.commit()
        return make_response(jsonify({
            'code': 200,
            'msg': 'success',
            'data': 'post liked'
        }), 200)
    else:
        # update the likes in post table
        post_info = db.query(Post).filter(Post.id == post_id).first()
        if post_info is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'post not exist'
            }), 400)
        # the user has liked the post, delete the like
        db.delete(post_like_info)
        db.commit()
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



@bp_posts.route('/posts/<int:board_id>', methods=['GET'])
@jwt_required()
def get_all_posts(board_id):
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
    db = get_db()
    posts_info = db.query(Post.id, Post.title, Post.body, Post.created, Post.author_id, Boards.board_name,
                          Post.likes).join(Boards, Post.board_id == Boards.id).filter(Boards.id == board_id).all()
    if posts_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'posts not exist'
        }), 400)
    posts = []
    for post_info in posts_info:
        # get user name from post_info.author
        author_name = db.query(User.username).filter(User.id == post_info.author_id).first()
        posts.append({
            'id': post_info.id,
            'title': post_info.title,
            'body': post_info.body,
            'created': post_info.created,
            'username': author_name.username,
            'board_name': post_info.board_name,
            'likes': post_info.likes
        })
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': posts
    }), 200)



@bp_posts.route('/comments', methods=['POST'])
@jwt_required()
def new_comments():
    # add a comment
    body = request.json.get('body')
    board_id = int(request.json.get('board_id'))
    post_id = int(request.json.get('post_id'))
    # board_id = 1  -> arxiv, 2 -> top universities
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
    if post_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing post_id in request body'
        }), 400)
    db = get_db()
    user_email = get_jwt_identity()
    # get user_id
    stmt = select(User).where(User.email == user_email)
    user = db.scalar(stmt)
    if user is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'comment not exist'
        }), 400)

    # check if the post exists
    post_info = db.query(Post).filter(Post.id == post_id, Post.board_id == board_id).first()
    if post_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'post not exist'
        }), 400)

    user_id = user.id
    comment = Comment(author_id=user_id, board_id=board_id, post_id=post_id,
                      created=datetime.datetime.utcnow(), body=body, likes=0)
    if comment is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'add comment failed'
        }), 400)
    db.add(comment)
    db.commit()
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': 'comment added'
    }), 200)


@bp_posts.route('/comments/<int:board_id>', methods=['GET'])
@jwt_required()
def get_all_comments(board_id):
    # get all comments
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
    db = get_db()
    comments_info = db.query(Comment.id, Comment.body, Comment.created, Comment.author_id, Comment.likes,
                             User.username).join(User, Comment.author_id == User.id).filter(Comment.board_id == board_id).all()
    if comments_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'comments not exist'
        }), 400)
    comments = []
    for comment_info in comments_info:
        comments.append({
            'id': comment_info.id,
            'body': comment_info.body,
            'created': comment_info.created,
            'username': comment_info.username,
            'likes': comment_info.likes
        })
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': comments
    }), 200)


@bp_posts.route('/comments/<int:board_id>/<int:post_id>', methods=['GET'])
@jwt_required()
def get_comments(board_id, post_id):
    # get all comments
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
    comments_info = db.query(Comment.id, Comment.body, Comment.created, Comment.author_id, Comment.likes,
                             User.username).join(User, Comment.author_id == User.id).filter(Comment.post_id == post_id,
                                                                                            Comment.board_id == board_id).all()
    if comments_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'comments not exist'
        }), 400)
    comments = []
    for comment_info in comments_info:
        comments.append({
            'id': comment_info.id,
            'body': comment_info.body,
            'created': comment_info.created,
            'username': comment_info.username,
            'likes': comment_info.likes
        })
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': comments
    }), 200)


@bp_posts.route('/like_comment', methods=['POST'])
@jwt_required()
def like_comment():
    board_id = int(request.json.get('board_id'))
    comment_id = int(request.json.get('comment_id'))
    # get all comments
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
    if comment_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing comment_id in request'
        }), 400)
    db = get_db()
    # consider the case that the user has already liked the comment, if so, delete the like
    # check if the user has already liked the comment
    user_email = get_jwt_identity()
    # get user_id
    stmt = select(User).where(User.email == user_email)
    user = db.scalar(stmt)
    user_id = user.id
    comment_like_info = db.query(CommentLike).filter(CommentLike.user_id == user_id, CommentLike.comment_id == comment_id,
                                                     CommentLike.board_id == board_id).first()
    if comment_like_info is None:
        # the user has not liked the comment, add a like
        comment_like = CommentLike(user_id=user_id, comment_id=comment_id, board_id=board_id,
                                   created=datetime.datetime.utcnow())
        if comment_like is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'comment not exist'
            }), 400)
        # update the likes in comment table
        comment_info = db.query(Comment).filter(Comment.id == comment_id, Comment.board_id == board_id).first()
        if comment_info is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'comment not exist'
            }), 400)
        db.add(comment_like)
        db.commit()
        comment_info.likes = comment_info.likes + 1
        db.commit()
        return make_response(jsonify({
            'code': 200,
            'msg': 'success',
            'data': 'comment liked'
        }), 200)
    else:
        # update the likes in comment table
        comment_info = db.query(Comment).filter(Comment.id == comment_id, Comment.board_id == board_id).first()
        if comment_info is None:
            return make_response(jsonify({
                'code': 400,
                'msg': 'error',
                'data': 'comment not exist'
            }), 400)
        # the user has liked the comment, delete the like
        db.delete(comment_like_info)
        db.commit()
        comment_info.likes = comment_info.likes - 1
        db.commit()
        return make_response(jsonify({
            'code': 200,
            'msg': 'success',
            'data': 'comment unliked'
        }), 200)


@bp_posts.route('/like_comment/<int:board_id>/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_like_comment(board_id, comment_id):
    # get all comments
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
    if comment_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'Missing comment_id in request'
        }), 400)
    db = get_db()
    # get the number of likes
    comment_info = db.query(Comment.likes).filter(Comment.id == comment_id, Comment.board_id == board_id).first()
    if comment_info is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'comment not exist'
        }), 400)
    return make_response(jsonify({
        'code': 200,
        'msg': 'success',
        'data': comment_info.likes
    }), 200)