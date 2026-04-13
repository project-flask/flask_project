from flask import Blueprint, render_template

bp = Blueprint('items', __name__, url_prefix='/items')

# 글쓰기
@bp.route('/product-upload/')
def product_upload():
    return render_template('items/write.html')

# 상품 상세페이지
@bp.route('/product-details/')
def product_details():
    return render_template('items/PDP.html')

# 카테고리별 페이지
@bp.route('/product-categories/<int:category_id>')
def product_categories(category_id):
    return render_template('items/CP.html', category_id = category_id)