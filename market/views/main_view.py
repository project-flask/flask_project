from flask import Blueprint, render_template

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('main.html', items=items)

