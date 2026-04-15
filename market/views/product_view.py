
from datetime import datetime  # 날짜 기능을 쓰기 위해 추가
from flask import Blueprint, render_template, request, url_for, redirect # request 추가
from market import db  # db.session을 쓰기 위해 추가
from market.models import Item, Comment  # Comment 모델 추가 (4개코드 오늘 수정함 4월14일)

bp = Blueprint('items', __name__, url_prefix='/items')

# 글쓰기
@bp.route('/product-upload/')
def product_upload():
    return render_template('items/write.html')

#카테고리에 맞는 라우트 생성(4월15일 merge후 categori_id를 찾을 수 없어 임시생성)
@bp.route('/categories/<int:category_id>')
def product_categories(category_id):
    items = Item.query.filter_by(category_id=category_id, is_deleted=False).all()
    return render_template(
        'items/product_categories.html',
        category_id=category_id,
        items=items
    )