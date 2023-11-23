from flask import jsonify, Blueprint

__all__ = ['user_api']

user_api = Blueprint('user_api', __name__)


@user_api.get('/test/')
def print_test():
    ret = ['123', '456', '789']
    return jsonify(ret)

