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

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.dirname(__file__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'market.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extension 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # csrf 방지용 SECRET_KEY 지정
    SECRET_KEY = 'dev'
    app.config['SECRET_KEY'] = SECRET_KEY

    # Category 정보 DB에서 꺼내옴
    from market.models import Category, ItemStatus

    @app.context_processor
    def get_categories():
        categories = Category.query.order_by(Category.id.asc()).all()
        return dict(all_categories=categories)

    @app.context_processor
    def get_status():
        status = ItemStatus.query.order_by(ItemStatus.id.asc()).all()
        return dict(all_status=status)

    # footer 입력 데이터 ( 코드 재사용 전용 )
    @app.context_processor
    def inject_footer_data():
        footer_modals = [
            # 이용약관
            {'slug': 'rules',
             'title': '이용약관',
             'content': '<p>중고거래 사이트 REBORN</p>\
             <p>다시 태어났다는 뜻으로 순환구조 디자인 ribbon과 발음을 같게 하여 중고거래의 순환기능을 통해 필요없던 물건이 새로운 사용자에게서 새로 태어났다는 의미를 갖고있습니다.</p>'
            },
            # 개인정보처리방침
            {'slug': 'privacy',
             'title': '개인정보처리방침',
             'content': '<p>개인정보 감사합니다</p>'
             },
            # 운영정책
            {'slug': 'policy',
             'title': '운영정책',
             'content': '<p>운영정책 컨텐츠 영역</p>'
             },
            # 이용자보호 비전과 계획
            {'slug': 'vision',
             'title': '이용자보호 비전과 계획',
             'content': '<p>비전과 계획 모두 없습니다</p>'
             },
            # 청소년보호정책
            {'slug': 'youth',
             'title': '청소년보호정책',
             'content': '<p>청소년보호정책 컨텐츠 영역</p>'
             }
        ]

        return dict(footer_modals=footer_modals)

    # 모델 등록
    from . import models

    # DB 생성 + Seed 데이터
    with app.app_context():
        db.create_all()      # 테이블 없으면 생성
        #init_item_status()   # 상품 상태 기본 데이터 삽입


    # Blueprint 등록
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
