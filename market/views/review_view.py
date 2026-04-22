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

    # 내가 이 판매자와 거래한 completed deal들 조회
    deals = Deal.query.filter_by(
        seller_id=seller.id,
        buyer_id=g.user.id,
        deal_status='completed'
    ).all()

    if not deals:
        flash('리뷰를 작성할 권한이 없습니다.')
        return redirect(url_for('personal.seller_profile', user_id=user_id))

    # 아직 리뷰를 작성하지 않은 거래 하나 찾기
    target_deal = None
    for deal in deals:
        existing_review = Review.query.filter_by(
            deal_id=deal.id,
            reviewer_id=g.user.id
        ).first()

        if not existing_review:
            target_deal = deal
            break

    if not target_deal:
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
            deal_id=target_deal.id,
            created_at=datetime.now()
        )

        db.session.add(new_review)
        db.session.commit()

        flash('리뷰가 등록되었습니다.')
        return redirect(url_for('personal.seller_profile', user_id=user_id, tab='review'))

    return redirect(url_for('personal.seller_profile', user_id=user_id, tab='review'))