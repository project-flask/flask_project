from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()    # ORM 도구
migrate = Migrate()  # 테이블 구조 변경 시 DB에 반영해주는 도구

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.dirname(__file__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'market.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)


    SECRET_KEY = 'dev'
    app.config['SECRET_KEY'] = SECRET_KEY

    from . import models

    # 블루프린트
    from .views import main_view, auth_view, product_view, favorite_view, deal_view, review_view  # view 파일들 임포트
    app.register_blueprint(main_view.bp)
    app.register_blueprint(auth_view.bp) # 회원가입/로그인 블루프린트
    app.register_blueprint(favorite_view.bp)
    app.register_blueprint(deal_view.bp)
    app.register_blueprint(review_view.bp)


    return app