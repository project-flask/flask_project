from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev'

    BASE_DIR = os.path.dirname(__file__)


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # from . import models

    # 블루프린트
    from .views import main_view, auth_view, product_view, favorite_view, deal_view, review_view  # view 파일들 임포트
    app.register_blueprint(main_view.bp)
    app.register_blueprint(auth_view.bp) # 회원가입/로그인 블루프린트
    app.register_blueprint(favorite_view.bp)
    app.register_blueprint(deal_view.bp)
    app.register_blueprint(review_view.bp)

    return app