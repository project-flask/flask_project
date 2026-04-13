from flask import Blueprint, redirect, url_for, render_template
from market.models import Item

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('main.html')

@bp.route('/detail/<item_id>/')  # 1. 주소 뒤에 상품 ID를 받도록 설정합니다.
def detail(item_id):
    # 2. DB에서 ID에 해당하는 상품 정보를 하나 가져옵니다.
    product = Item.query.get_or_404(item_id)

    # 3. [추가] DB에서 전체 상품 목록을 가져옵니다 (최신순 6개)
    # .limit(6)을 붙여서 딱 6개만 가져오게 조절할 수 있습니다.
    item_list = Item.query.order_by(Item.item_reg_datetime.desc()).limit(6).all()

    # [데이터 가공] 날짜 형식을 미리 문자로 바꿉니다.
    formatted_date = product.item_reg_datetime.strftime('%Y-%m-%d %H:%M')

    # 4. 가져온 데이터를 'product'라는 이름으로 HTML에 전달합니다.
    return render_template('detail.html', product=product, formatted_date=formatted_date, item_list=item_list)
