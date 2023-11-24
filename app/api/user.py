from flask import jsonify, Blueprint
from sqlalchemy.orm import Session
from app.model.user import User

__all__ = ['user_api']

user_api = Blueprint('user_api', __name__)


@user_api.get('/test/')
def print_test():
    ret = ['123', '456', '789']
    return jsonify(ret)


@user_api.post('/')
def create_user(db: Session, user: User):
    # fake_hashed_password = user.password + "notreallyhashed"
    # db_user = User(email=user.email, hashed_password=fake_hashed_password)
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    return jsonify("good create")
