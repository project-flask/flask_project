from flask import Blueprint, render_template

bp = Blueprint('items', __name__)

@bp.route('/product-details')
def product_details():
    return render_template('items/PDP.html')