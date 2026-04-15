# import 추가 4월15일 수정
from flask import Blueprint, render_template, g, request, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from market import db
from market.views.auth_view import login_required
from market.models import Item, Favorite, Review

bp = Blueprint('mypage', __name__, url_prefix='/mypage')


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
# 회원정보변경 4월15일 생성
@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = g.user

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.phone = request.form['phone']

        db.session.commit()
        flash('회원정보가 저장되었습니다.')

    return render_template('personal/edit_profile.html', user=user)
# 비밀번호 변경 페이지로 이동 4월 15일 생성
@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = g.user

    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not current_password or not new_password or not confirm_password:
            flash('모든 항목을 입력해주세요.')
            return render_template('personal/change_password.html', user=user)

        if not check_password_hash(user.password, current_password):
            flash('현재 비밀번호가 올바르지 않습니다.')
            return render_template('personal/change_password.html', user=user)

        if new_password != confirm_password:
            flash('새 비밀번호와 비밀번호 확인이 일치하지 않습니다.')
            return render_template('personal/change_password.html', user=user)

        if len(new_password) < 8:
            flash('새 비밀번호는 8자 이상 입력해주세요.')
            return render_template('personal/change_password.html', user=user)

        if check_password_hash(user.password, new_password):
            flash('현재 비밀번호와 다른 비밀번호를 입력해주세요.')
            return render_template('personal/change_password.html', user=user)

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash('비밀번호가 변경되었습니다.')
        return redirect(url_for('mypage.change_password'))


    return render_template('personal/change_password.html', user=user)