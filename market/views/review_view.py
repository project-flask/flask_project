from flask import Blueprint, request, redirect, url_for, flash, g
from market.views.auth_view import login_required
from market import db
from market.models import Review, Deal, User
from datetime import datetime

bp = Blueprint('review', __name__, url_prefix='/review')


@bp.route('/create/<int:user_id>/', methods=['GET', 'POST'])
@login_required
def create_review(user_id):
    seller = User.query.get_or_404(user_id)

    # 내가 이 판매자의 구매자인지 확인
    deal = Deal.query.filter_by(
        seller_id=seller.id,
        buyer_id=g.user.id,
        deal_status='completed'
    ).first()

    if not deal:
        flash('리뷰를 작성할 권한이 없습니다.')
        return redirect(url_for('personal.seller_profile', user_id=user_id))

    # 이미 작성했는지 확인
    existing_review = Review.query.filter_by(
        deal_id=deal.id,
        reviewer_id=g.user.id
    ).first()

    if existing_review:
        flash('이미 리뷰를 작성한 거래입니다.')
        return redirect(url_for('personal.seller_profile', user_id=user_id, tab='review'))

    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if not content:
            flash('리뷰 내용을 입력해주세요.')
            return redirect(url_for('personal.seller_profile', user_id=user_id, tab='review'))

        new_review = Review(
            content=content,
            reviewer_id=g.user.id,
            target_user_id=seller.id,
            deal_id=deal.id,
            created_at=datetime.now()
        )

        db.session.add(new_review)
        db.session.commit()

        flash('리뷰가 등록되었습니다.')
        return redirect(url_for('personal.seller_profile', user_id=user_id, tab='review'))

    return redirect(url_for('personal.seller_profile', user_id=user_id, tab='review'))