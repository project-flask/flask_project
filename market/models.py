from market import db
from datetime import datetime

# [1. 유저 모델]
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(50), unique=True, index=True)  # 로그인 아이디
    username = db.Column(db.String(50), unique=True, nullable=False)  # 닉네임
    password = db.Column(db.String(200))
    email = db.Column(db.String(50), unique=True, index=True)
    phone = db.Column(db.String(20), unique=True)

    # 관계 설정: seller라는 이름으로 상품에서 유저 정보 불러옴
    items = db.relationship('Item', backref='seller', lazy=True, cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # 관리자 여부 확인용 (기본값은 일반유저 'user')
    role = db.Column(db.Enum('user', 'admin', name='user_roles'), default='user')



# [2. 상품 모델 통합 버전]
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_title = db.Column(db.String(100), nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    item_description = db.Column(db.String(500))

    # --- 팀원들 코드에서 가져온 부분 ---
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('item_status.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # 1. 판매자 연결 (외래키 및 관계 설정)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('item_set'))

    # 2. 가격 음수 방지 제약조건 및 테이블 설정
    __table_args__ = (
        db.CheckConstraint('item_price >= 0', name='check_price_positive'),
        {'extend_existing': True} # 중복 정의 에러 방지용 안전장치
    )



# [3. 상품 상태 모델]
class ItemStatus(db.Model):
    __tablename__ = 'item_status'
    id = db.Column(db.Integer, primary_key=True)
    item_status = db.Column(db.String(100), unique=True)  # 판매중, 예약중, 판매완료 등

    # status라는 이름으로 상품에서 상태 정보 불러옴
    items = db.relationship('Item', backref='status', lazy=True)


# [4. 카테고리 모델]
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True)

    # category라는 이름으로 상품에서 카테고리 정보 불러옴
    items = db.relationship('Item', backref='category', lazy=True)


# [5. 찜하기 모델]
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)

    # 관계 설정: 유저는 favorites로, 상품은 favorited_by로 접근 가능
    user = db.relationship('User', backref='favorites')
    item = db.relationship('Item', backref='favorited_by')

    # 한 유저가 같은 상품을 중복으로 찜 못하게 막는 제약조건
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_id', name='unique_favorite'),
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())



# [6. 리뷰 모델]
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    content = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # 작성자와 리뷰 대상자 관계 설정
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='written_reviews')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='received_reviews')


# [7. 상품 이미지 모델]
class ItemImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(300))

# 댓글정보테이블 4월15일 수정함
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)


    # 어떤 상품에 달린 댓글인지 연결 (Foreign Key)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'))
    item = db.relationship('Item', backref=db.backref('comment_set'))
    # --- 여기부터 새로 추가할 내용 4월15일 ---
    # 1. 작성자(User)의 번호를 저장할 칸 (Foreign Key)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    # 2. 작성자 모델과 직접 연결 (관계 설정)
    # backref='comment_set'을 쓰면 유저가 쓴 모든 댓글을 user.comment_set으로 가져올 수 있습니다.
    user = db.relationship('User', backref=db.backref('comment_set'))

