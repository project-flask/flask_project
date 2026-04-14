from flask import Flask
from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy

import os

from sqlalchemy import MetaData

naming_convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


# Extension 객체 생성

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))     # ORM 도구
migrate = Migrate()   # 테이블 구조 변경(DB migration) 관리

# Seed 데이터 (초기 데이터)

def init_item_status():
    from market.models import ItemStatus
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


    # Blueprint 등록(오늘수정)
    from .views import (
        main_view,
        auth_view,
        product_view,
        mypage_view,
 #       favorite_view,
#        deal_view,
 #       review_view,
    )

    app.register_blueprint(main_view.bp)      # 메인 페이지
    app.register_blueprint(auth_view.bp)      # 회원가입 / 로그인
    app.register_blueprint(product_view.bp)   # 상품
    app.register_blueprint(mypage_view.bp)    # 마이 페이지
    # app.register_blueprint(favorite_view.bp)  # 찜
    # app.register_blueprint(deal_view.bp)      # 거래
    # app.register_blueprint(review_view.bp)    # 리뷰

    return app



