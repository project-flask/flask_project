# import 추가 4월15일 수정
from flask import Blueprint, render_template, g, request, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from market import db
from market.views.auth_view import login_required
from market.models import Item, Favorite, Review, User

# 경로 수정으로 인해 삭제 4월16일
bp = Blueprint('personal', __name__, url_prefix='/personal')


# 마이페이지
@bp.route('/mypage/')
@login_required
def my_page():
    user = g.user

    products = Item.query.filter_by(user_id=user.id)\
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

# 회원정보변경 4월16일 수정

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = g.user

    if request.method == 'POST':
        action = request.form.get('action')

        user.username = request.form['username']
        user.email = request.form['email']
        user.phone = request.form['phone']

        new_nickname = request.form.get('nickname', '').strip()

        if not new_nickname:
            flash('닉네임을 입력해주세요.')
            return render_template('personal/edit_profile.html', user=user)

        if len(new_nickname) > 10:
            flash('닉네임은 10자 이하로 입력해주세요.')
            return render_template('personal/edit_profile.html', user=user)

        #중복체크 4월16일 생성
        existing_user = User.query.filter_by(nickname=new_nickname).first()
        if existing_user and existing_user.id != user.id:
            flash('이미 사용 중인 닉네임입니다.')
            return render_template('personal/edit_profile.html', user=user)

        user.nickname = new_nickname
        user.email = request.form.get('email', '').strip()
        user.phone = request.form.get('phone', '').strip()

        if action == 'cancel':
            flash('수정이 취소되었습니다.')
            return redirect(url_for('personal.my_page'))

        elif action == 'save':
            db.session.commit()
            flash('회원정보가 저장되었습니다.')
            return redirect(url_for('personal.my_page'))

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

        #경로수정 4월16일
        return redirect(url_for('personal.my_page'))

    return render_template('personal/change_password.html', user=user)

# 찜 목록
@bp.route('/favorite/')
@login_required
def favorite():
    return render_template('personal/favorite.html',
                           wishes=g.user.favorites)

# 판매자 공개정보 4월16일 생성
@bp.route('/seller/<int:user_id>/')
def seller_profile(user_id):
    seller = User.query.get_or_404(user_id)

    products = Item.query.filter_by(user_id=seller.id)\
        .order_by(Item.created_at.desc()).all()

    reviews = Review.query.filter_by(target_user_id=seller.id)\
        .order_by(Review.created_at.desc()).all()

    return render_template(
        'personal/seller_profile.html',
        seller=seller,
        products=products,
        reviews=reviews
    )
# 상태메시지 저장 4월16일 생성
@bp.route('/status-message', methods=['POST'])
@login_required
def update_status_message():
    user = g.user
    new_status = request.form.get('status_message', '').strip()

    if len(new_status) > 50:
        flash('상태 메시지는 50자 이하로 입력해주세요.')
        return redirect(url_for('personal.my_page'))

    user.status_message = new_status
    db.session.commit()
    flash('상태 메시지가 저장되었습니다.')

    return redirect(url_for('personal.my_page'))