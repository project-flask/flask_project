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



# [2. 상품 모델]
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_title = db.Column(db.String(100), nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    item_description = db.Column(db.String(500))

    # 외래키 연결
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('item_status.id'), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

# 상품 (4월14일 수정함)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_title = db.Column(db.String(100), unique=False) # 상품 제목
    item_price = db.Column(db.Integer) # 가격
    item_reg_datetime = db.Column(db.DateTime(), unique = False) # 상품 업로드 시간
    item_description = db.Column(db.String(500)) # 상품 내용
    # 어떤 유저가 올린 상품인지 연결 (외래키)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('item_set'))


    # 가격 음수 방지 제약조건
    __table_args__ = (
        db.CheckConstraint('item_price >= 0', name='check_price_positive'),
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

# 댓글정보테이블
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)

    # 어떤 상품에 달린 댓글인지 연결 (Foreign Key)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'))
    item = db.relationship('Item', backref=db.backref('comment_set'))

    # (선택) 작성자 기능이 있다면 추가
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


    # images라는 이름으로 상품에서 여러 장의 이미지를 불러냄
    item = db.relationship('Item', backref='images')