
from flask import Blueprint, render_template, request, url_for, redirect, g
from market.views.auth_view import login_required
from market import db
from market.models import Item, Category, Comment

from datetime import datetime  # 날짜 기능을 쓰기 위해 추가



bp = Blueprint('items', __name__, url_prefix='/items')

# 글쓰기
@bp.route('/product-upload/', methods=['GET', 'POST'])
@login_required
def product_upload():

    if request.method == 'POST':
        # HTML 폼에서 보낸 데이터 읽어옴
        title = request.form.get('subject')
        price = request.form.get('price')
        content = request.form.get('content')
        category_id = request.form.get('category')
        status_id = request.form.get('status')

        # 가격 예외처리
        try:
            # 콤마(,)가 포함되어 있을 수도 있으니 제거하고 숫자로 변환
            clean_price = str(price).replace(',', '').strip()
            item_price = int(clean_price) if clean_price else 0
        except ValueError:
            item_price = 0  # 숫자가 아니면 그냥 0원 처리

        # 카테고리 예외처리
        try:
            cat_id = int(category_id) if category_id else 21  # 기본값 기타
        except ValueError:
            cat_id = 21

        # 상품 상태 예외처리
        try:
            st_id = int(status_id) if status_id else 3
        except ValueError:
            st_id = 3

        # DB에 저장할 객체 만들기
        if title:
            new_item = Item(
                item_title = title,
                item_price = item_price,
                item_description = content,
                user_id = g.user.id,
                category_id = cat_id,
                status_id = 1  # seed.py의 '판매중'을 기본 default 1번으로 가져옴
            )

            db.session.add(new_item)
            db.session.commit()

        # 등록 완료 후 메인으로 전달
        return redirect(url_for('main.index'))

    # GET 방식일 때
    categories = Category.query.all()
    return render_template('items/write.html', categories = categories)

# 상품 상세페이지
@bp.route('/product-details/<int:item_id>')
def product_details(item_id):
    # DB에서 해당 ID의 상품 하나 가져옴
    item = Item.query.get_or_404(item_id)
    return render_template('items/PDP.html', item = item)

# 카테고리별 페이지
@bp.route('/product-categories/<int:category_id>')
def product_categories(category_id):
    cat = Category.query.get_or_404(category_id)
    # DB에서 해당 카테고리 상품만 필터링해서 가져옴
    category_items = Item.query.filter_by(category_id=category_id).all()
    return render_template('items/CP.html', category_id = category_id, title = cat.category_name, items = category_items)

# 필터링 (거래 가능한 상품만 보기) 페이지
@bp.route('/product-status/<int:item_status_id>')
def product_statuses(item_status_id):
    item_statuses = Item.query.filter_by(status_id=item_status_id).all()
    return render_template('items/CP.html', items = item_statuses, title = "거래 가능 상품")
