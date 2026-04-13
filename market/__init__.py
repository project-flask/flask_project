from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import os


# Extension 객체 생성

db = SQLAlchemy()     # ORM 도구
migrate = Migrate()   # 테이블 구조 변경(DB migration) 관리

# Seed 데이터 (초기 데이터)

def init_item_status():
    """
    상품 상태 기본값 생성
    앱 최초 실행 시 DB에 자동 삽입됨
    """
    from .models import ItemStatus

    # 이미 데이터 있으면 생성 안함 (중복 방지)
    if not ItemStatus.query.first():
        db.session.add_all([
            ItemStatus(item_status='판매중'),
            ItemStatus(item_status='예약중'),
            ItemStatus(item_status='판매완료'),
        ])
        db.session.commit()

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.dirname(__file__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'market.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Extension 초기화
    
    db.init_app(app)
    migrate.init_app(app, db)



    SECRET_KEY = 'dev'
    app.config['SECRET_KEY'] = SECRET_KEY

    # 모델 등록
    from . import models


    # DB 생성 + Seed 데이터
    with app.app_context():
        db.create_all()      # 테이블 없으면 생성
        init_item_status()   # 상품 상태 기본 데이터 삽입


    # Blueprint 등록

    from .views import (
        main_view,
        auth_view,
        product_view,
        favorite_view,
        deal_view,
        review_view,
    )

    app.register_blueprint(main_view.bp)      # 메인 페이지
    app.register_blueprint(auth_view.bp)      # 회원가입 / 로그인
    app.register_blueprint(product_view.bp)   # 상품
    app.register_blueprint(favorite_view.bp)  # 찜
    app.register_blueprint(deal_view.bp)      # 거래
    app.register_blueprint(review_view.bp)    # 리뷰

    return app