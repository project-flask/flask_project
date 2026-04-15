from market import db

# 유저
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(50), unique=True, index=True, nullable=False)  # 로그인용, 로그인 속도 개선
    username = db.Column(db.String(50), nullable=False)  # 닉네임 중복, 공란 방지
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False) # 이메일
    phone = db.Column(db.String(20), unique=True, nullable=True)
    items = db.relationship('Item', backref='seller', lazy=True, cascade="all, delete-orphan") # 상품과 양방향 접근, 유저 삭제시 상품 자동 삭제
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True) # 생성 시간
    # 관리자 속성
    role = db.Column(
        db.Enum('user', 'admin', name='user_roles'),
        default='user', nullable=False
    )




# 상품
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_title = db.Column(db.String(100), unique=False, nullable=False) # 상품 제목
    item_price = db.Column(db.Integer, nullable=False) # 가격 문자열이 아니라 숫자형으로 수정

    item_description = db.Column(db.String(500)) # 상품 내용
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False) # 상품에 판매자 등록, 판매자 삭제 → 상품 삭제 → 이미지/찜 자동 정리
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 카테고리와 연결
    status_id = db.Column(db.Integer, db.ForeignKey('item_status.id'), nullable=False, default=1) # 판매 상태 (판매중 / 예약중 / 판매완료)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)  # 상품 업로드 시간
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)  # 상품삭제시 거래가 깨질 위험이 있으니 숨김처리
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
    # 상품 가격 음수 방지
    __table_args__ = (
        db.CheckConstraint('item_price >= 0', name='check_price_positive'),
    )
    # item_image랑 연결
    images = db.relationship(
        'ItemImage',
        back_populates='item',
        cascade="all, delete-orphan"
    )


# 상품 상태
class ItemStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_status = db.Column(db.String(100), unique=True, nullable=False)  # 상품 상태
    items = db.relationship('Item', backref='status', lazy=True) # 상품과 양방향 접근



# 카테고리
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('Item', backref='category', lazy=True) # 상품과 양방향 접근

# 찜하기
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True) # 유저 삭제시 자동삭제
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False, index=True) # 유저 삭제시 자동삭제
    user = db.relationship('User', backref='favorites')     # 유저와 상품과 양방향
    item = db.relationship('Item', backref='favorited_by')
    #  중복 찝 방지
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_id', name='unique_favorite'),
        db.Index('idx_favorite_user_item', 'user_id', 'item_id')
    )
    # 찜한 시간
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )



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

# 거래
class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)  # 판매자 삭제 시 거래기록 유지

    deal_datetime = db.Column(db.DateTime, nullable=True)
    deal_price = db.Column(db.Integer, nullable=False)

    # 거래 상태
    deal_status = db.Column(
        db.Enum('requested', 'completed', 'cancelled', name='deal_status'),
        default='requested', nullable=False
    )
    # 거래 완료 시간
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(), index=True
    )
    # deal_price의 음수방지
    __table_args__ = (
        db.CheckConstraint('deal_price >= 0', name='check_deal_price_positive'),
    )
    item = db.relationship('Item', backref='deals')  # 상품과 양방향
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')  # 구매자 정보
    seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')
    # service에서만 상태변환이 가능하게
    ALLOWED_TRANSITIONS = {
        'requested': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': []

    }

# 리뷰
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False) # 구매자만 리뷰를 쓸 수 있게
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))  # 유저 삭제시 기록 유지

    content = db.Column(db.String(300), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)  # 리뷰 작성 시간

    reviewer = db.relationship(
        'User',
        foreign_keys=[reviewer_id],
        backref='written_reviews'
    )
    #  작성자 / 리뷰 대상 유저와 양방향 연결
    target_user = db.relationship(
        'User',
        foreign_keys=[target_user_id],
        backref='received_reviews'
    )
    deal = db.relationship('Deal', backref='reviews')
    __table_args__ = (db.UniqueConstraint('reviewer_id', 'deal_id', name='unique_review_per_deal'),)  # 같은 거래에 리뷰 중복 방지

# 상품사진 1장이상 가능
class ItemImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(
        db.Integer,
        db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False
    )
    # item.images 가능
    image_url = db.Column(db.String(300), nullable=False)
    item = db.relationship('Item', back_populates='images')



