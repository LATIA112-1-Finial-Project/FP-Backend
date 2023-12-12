import os

from flask import Flask
from flask_argon2 import Argon2
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import timedelta
from flask_cors import CORS

mail = Mail()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # app.config['FRONTEND_URL'] = "https://latiafp-frontend.subarya.me"
    app.config['FRONTEND_URL'] = "http://localhost:5173"

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from .api import user_setting
    app.register_blueprint(user_setting.bp_uni)

    from .api import arxiv
    app.register_blueprint(arxiv.bp_arxiv)

    mail.init_app(app)
    app.config['MAIL'] = mail

    Argon2(app)

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    JWTManager(app)

    # from . import blog
    # app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')

    return app
