
from flask import Blueprint, render_template, g, redirect, url_for
from market.views.auth_view import login_required
from market.models import Item, Favorite, Review


bp = Blueprint('personal', __name__, url_prefix='/personal')


# 마이페이지
@bp.route('/mypage/')
@login_required
def my_page():
    if g.user:
        return render_template('personal/mypage.html',
                           user=g.user,
                           products=g.user.items,    # 유저가 올린 상품
                           wishes=g.user.favorites,  # 유저가 찜한 목록
                           reviews=g.user.received_reviews) # 받은 리뷰
    else:
        return redirect(url_for('auth.login'))

# 찜 목록
@bp.route('/favorite/')
@login_required
def favorite():
    return render_template('personal/favorite.html',
                           wishes=g.user.favorites)

@bp.route('/')
@login_required
def mypage():
    user = g.user

    products = Item.query.filter_by(user_id=user.id, is_deleted=False)\
        .order_by(Item.created_at.desc()).all()

    wishes = Favorite.query.filter_by(user_id=user.id)\
        .order_by(Favorite.created_at.desc()).all()

    reviews = Review.query.filter_by(target_user_id=user.id)\
        .order_by(Review.created_at.desc()).all()

    return render_template(
        'personal/mypage.html',
        user=user,
        products=products,
        wishes=wishes,
        reviews=reviews
    )
