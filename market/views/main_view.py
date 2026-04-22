from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from market.models import Item, Category

bp = Blueprint('main', __name__, url_prefix='/')


# 인트로 페이지 (주소: /)
@bp.route('/')
def landing():
    # 이미 로그인한 상태면(로그인 세션이 남아있으면)바로 상품 페이지(/home)로 보냄
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # 로그인 세션 없는 사용자는 intro.html 보여줌
    return render_template('intro.html')


# 실제 상품 목록 페이지 (주소: /home)
@bp.route('/home')
def index():
    all_categories = Category.query.all()
    product_list = Item.query.filter(
        Item.is_deleted == False
    ).order_by(Item.created_at.desc()).all()

    return render_template('main.html', product_list=product_list, all_categories=all_categories)