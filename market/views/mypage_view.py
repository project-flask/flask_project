# import 추가 4월21일 수정
import os
import re
import uuid

from flask import Blueprint, render_template, g, request, flash, redirect, url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from market import db
from market.views.auth_view import login_required
from market.models import Item, Favorite, Review, User, ItemStatus, Deal

# 경로 수정으로 인해 삭제 4월16일
bp = Blueprint('personal', __name__, url_prefix='/personal')

# 마이페이지
@bp.route('/mypage/')
@login_required
def my_page():
    user = g.user
    # 판매중인 상품수로 변경 4월20일
    products = Item.query.join(ItemStatus).filter(
        Item.user_id == user.id,
        Item.is_deleted == False,
        ItemStatus.item_status == '판매중'
    ).order_by(Item.created_at.desc()).all()

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

        if action == 'cancel':
            flash('수정이 취소되었습니다.')
            return redirect(url_for('personal.my_page'))

        elif action == 'save':
            # 검증방식 추가로 인해 수정 4월20일
            old_nickname = user.nickname
            new_nickname = request.form.get('nickname', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip().replace(' ', '')

            if not new_nickname:
                flash('닉네임을 입력해주세요.')
                return render_template('personal/edit_profile.html', user=user)

            if len(new_nickname) > 10:
                flash('닉네임은 10자 이하로 입력해주세요.')
                return render_template('personal/edit_profile.html', user=user)

            # 중복체크 4월20일 수정
            existing_user = User.query.filter_by(nickname=new_nickname).first()
            if existing_user and existing_user.id != user.id:
                flash('이미 사용 중인 닉네임입니다.')
                return render_template('personal/edit_profile.html', user=user)

            # 이메일 형식 검증하기 4월20일
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{3,}$'
            if not re.match(email_pattern, email):
                flash('올바른 이메일 형식을 입력해주세요.')
                return render_template('personal/edit_profile.html', user=user)

            # 전화번호 형식 검증하기 4월20일
            phone_pattern = r'^01[0-9]-?\d{3,4}-?\d{4}$'
            if not re.match(phone_pattern, phone):
                flash('올바른 전화번호 형식을 입력해주세요.')
                return render_template('personal/edit_profile.html', user=user)

            nickname_changed = (old_nickname != new_nickname)

            # 닉네임 바뀌었을 때 파일명 변경 예외처리
            if nickname_changed:
                old_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', old_nickname)
                new_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', new_nickname)

                if os.path.exists(old_folder):
                    os.rename(old_folder, new_folder)

                if user.profile_image:
                    user.profile_image = user.profile_image.replace(f'/static/uploads/profiles/{old_nickname}/',
                                                                    f'/static/uploads/profiles/{new_nickname}/')

            # 변수저장
            user.nickname = new_nickname
            user.email = email
            user.phone = phone

            # 프로필 이미지 처리 merge후 위치변경 때문에 수정 4월20일
            file = request.files.get('profile_image')

            if file and file.filename != '':
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', new_nickname)
                os.makedirs(upload_folder, exist_ok=True)

                # 중복 방지
                if user.profile_image:
                    # DB에 저장된 경로에서 파일명만 뽑아서 삭제
                    old_path = os.path.join(current_app.root_path, user.profile_image.lstrip('/'))
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = file.filename
                file.save(os.path.join(upload_folder, filename))

                # DB에 웹 경로 업데이트
                user.profile_image = f'/static/uploads/profiles/{new_nickname}/{filename}'

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
        # 8글자 제한 삭제 4월22일
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

# 판매자 공개정보 4월21일 수정
@bp.route('/seller/<int:user_id>/')
def seller_profile(user_id):
    seller = User.query.get_or_404(user_id)
    print(f"판매자 이미지 경로: {seller.profile_image}")
    tab = request.args.get('tab', 'products')

    products = Item.query.join(ItemStatus).filter(
        Item.user_id == seller.id,
        Item.is_deleted == False,
        ItemStatus.item_status == '판매중'
    ).order_by(Item.created_at.desc()).all()

    completed_products = Item.query.join(ItemStatus).filter(
        Item.user_id == seller.id,
        Item.is_deleted == False,
        ItemStatus.item_status == '판매완료'
    ).order_by(Item.created_at.desc()).all()

    completed_products_count = len(completed_products)

    reviews = Review.query.filter_by(target_user_id=seller.id)\
        .order_by(Review.created_at.desc()).all()

    # 특정 조건에서만 노출되게
    can_write_review = False

    if g.user:
        deals = Deal.query.filter_by(
            seller_id=seller.id,
            buyer_id=g.user.id,
            deal_status='completed'
        ).all()

        for deal in deals:
            existing_review = Review.query.filter_by(
                deal_id=deal.id,
                reviewer_id=g.user.id
            ).first()

            if not existing_review:
                can_write_review = True
                break

    return render_template(
        'personal/seller_profile.html',
        seller=seller,
        products=products,
        reviews=reviews,
        completed_products=completed_products,
        completed_products_count=completed_products_count,
        can_write_review=can_write_review,
        tab=tab
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

# 거래내역 페이지 4월20일 생성
@bp.route('/transactions/')
@login_required
def transaction_history():
    user = g.user

    selling_items = Item.query.join(ItemStatus).filter(
        Item.user_id == user.id,
        Item.is_deleted == False,
        ItemStatus.item_status == '판매중'
    ).order_by(Item.created_at.desc()).all()

    reserved_items = Item.query.join(ItemStatus).filter(
        Item.user_id == user.id,
        Item.is_deleted == False,
        ItemStatus.item_status == '예약중'
    ).order_by(Item.created_at.desc()).all()
    # 판매완료 목록에 구매자와 거래시간 표기 4월22일
    completed_deals = Deal.query.join(Item).join(ItemStatus).filter(
        Item.user_id == user.id,
        Item.is_deleted == False,
        ItemStatus.item_status == '판매완료',
        Deal.deal_status == 'completed'
    ).order_by(Deal.deal_datetime.desc()).all()

    # 구매 이력 추가 4월22일
    purchase_deals = Deal.query.filter(
        Deal.buyer_id == user.id,
        Deal.deal_status == 'completed'
    ).order_by(Deal.deal_datetime.desc()).all()

    return render_template(
        'personal/transaction_history.html',
        user=user,
        selling_items=selling_items,
        reserved_items=reserved_items,
        completed_deals=completed_deals,
        purchase_deals=purchase_deals,
    )