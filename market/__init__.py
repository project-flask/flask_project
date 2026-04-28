from flask import Flask
from datetime import timedelta   # 로그인 세션 1시간 유지용(4/17)
from flask_migrate import Migrate
from flask_login import LoginManager #intro 페이지용(4/20)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from .footer_content import footer_modals

import os

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
login_manager = LoginManager()  # Loginmanager객체 생성

def create_app():
    app = Flask(__name__)

    from .filter import format_datetime
    app.jinja_env.filters['format_datetime'] = format_datetime

    BASE_DIR = os.path.dirname(__file__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'market.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extension 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # LoginManager를 앱에 등록 (4/20)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 로그인 필요 시 이동할 페이지

   # 유저 로더 정의 (4/20 추가)
    from market.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # csrf 방지용 SECRET_KEY 지정
    SECRET_KEY = 'dev'
    app.config['SECRET_KEY'] = SECRET_KEY

    # 로그인 세션 유지 1시간 (4/17)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

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
        return dict(footer_modals=footer_modals)

    # 모델 등록
    from . import models

    # DB 생성 + Seed 데이터
    with app.app_context():
        db.create_all()      # 테이블 없으면 생성

        # 상품 상태, 카테고리 파일 (seed.py) 자동 호출
        try:
            from seed import seed_data
            seed_data()
            # Archive stored. # 성공
        except ImportError:
            pass

    # Blueprint 등록
    from .views import (
        main_view,
        auth_view,
        product_view,
        mypage_view,
        review_view,
    )

    app.register_blueprint(main_view.bp)      # 메인 페이지
    app.register_blueprint(auth_view.bp)      # 회원가입 / 로그인
    app.register_blueprint(product_view.bp)   # 상품
    app.register_blueprint(mypage_view.bp)    # 마이 페이지
    app.register_blueprint(review_view.bp)    # 리뷰

    return app
