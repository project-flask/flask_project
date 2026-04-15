from flask import Blueprint, render_template
from market.models import Item, Category


bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    all_categories = Category.query.all()
    product_list = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('main.html', product_list=product_list, all_categories=all_categories)