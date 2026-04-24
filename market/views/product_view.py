import os

from flask import Blueprint, render_template, request, url_for, redirect, g, flash, current_app
from market.views.auth_view import login_required
from market import db
from market.models import User, Item, Category, Comment, ItemStatus, ItemImage, Deal, Favorite
from werkzeug.utils import secure_filename

from datetime import datetime  # 날짜 기능을 쓰기 위해 추가

bp = Blueprint('items', __name__, url_prefix='/items')

# 검색 기능
@bp.route('/list/')
def _list():
    page = request.args.get('page', default='1', type=int)
    kw = request.args.get('kw', default='', type=str)

    # 삭제된 상품 필터링 후 페이지에서 제외
    item_list = Item.query.filter(Item.is_deleted == False)

    # 검색어에 따른 필터링
    if kw:
        search = f'%{kw}%'

        item_list = item_list.join(User).filter(
            Item.item_title.ilike(search) |              # 상품명
            Item.item_description.ilike(search) |        # 상품 내용
            User.username.ilike(search)                  # 상품 등록한 유저
        ).distinct()

    # 아이템 최신순 정렬
    item_list = item_list.order_by(Item.created_at.desc())

    # 한 페이지에 n개 정렬 (n 코드에서 수정해서 값 변경해도 됨)
    paging_obj = item_list.paginate(page=int(page), per_page=10)

    # 사이드바 카테고리 목록
    all_categories = Category.query.all()

    return render_template('items/item_list.html',
                           product_list = paging_obj,
                           all_categories = all_categories,
                           kw = kw,
                           page = page)

# 글쓰기
@bp.route('/product-upload/', methods=['GET', 'POST'])
@login_required
def product_upload():
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title', '')
        price = request.form.get('price', '')
        content = request.form.get('content', '')
        category_id = request.form.get('category', '')

        # 가격 예외처리, 음수 검증
        price_error = None
        try:
            clean_price = str(price).replace(',', '').strip()
            item_price = int(clean_price) if clean_price else 0
            if item_price < 0:
                price_error = '음수는 입력 불가능합니다.'
        except ValueError:
            item_price = 0  # 숫자가 아니면 그냥 0원 처리
            price_error = '숫자만 입력해주세요.'

        # 카테고리 예외처리
        try:
            cat_id = int(category_id) if category_id else 20  # 기본값 기타
        except ValueError:
            cat_id = 20

        errors = []
        # 상품 등록 시 빈 칸일 경우 메시지 출력
        if not title.strip():
            errors.append("상품명")
            flash('상품명을 입력해주세요.')

        if not category_id:
            errors.append("카테고리")
            flash('카테고리를 선택해주세요.')

        if not price.strip() or price_error:
            errors.append("가격")
            if price_error:
                flash(price_error)
            else:
                flash('가격을 입력해주세요.')

        if not content.strip():
            errors.append("상세 설명")
            flash('상품 설명을 입력해주세요.')

        if errors:
            # 입력 페이지로 이동
            return render_template('items/write.html',
                                   categories=categories,
                                   product=None,
                                   title=title,
                                   price=price,
                                   content=content,
                                   category_id=int(category_id) if category_id else None,
                                   errors=errors)

        # DB에 저장할 객체 만들기
        if title:
            new_item = Item(
                item_title = title,
                item_price = item_price,
                item_description = content,
                user_id = g.user.id,
                category_id = cat_id if 'cat_id' in locals() else int(category_id),
                status_id = 1,  # seed.py의 '판매중'을 기본 default 1번으로 가져옴
                created_at = datetime.utcnow()
            )

            db.session.add(new_item)
            # db에 미리 전달 후 new_item.id 확보
            db.session.flush()

            if 'images' in request.files:
                files = request.files.getlist('images')

                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                folder_name = f"{title}_{timestamp}"

                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', f'{g.user.nickname}', folder_name)
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path, exist_ok=True)

                for file in files:
                    if file and file.filename:
                        # 파일 이름 보안 처리
                        #filename = secure_filename(file.filename)
                        filename = file.filename
                        # 실제 서버 폴더에 저장
                        file.save(os.path.join(upload_path, filename))

                        # DB에 이미지 경로 기록 (ItemImage 모델 활용)
                        web_path = f'/static/uploads/products/{g.user.nickname}/{folder_name}/{filename}'
                        new_img = ItemImage(item_id=new_item.id, image_url=web_path)
                        db.session.add(new_img)

            db.session.commit()
            flash("상품이 성공적으로 등록되었습니다!", "success")

            # 등록 완료 후 메인으로 전달
            return redirect(url_for('main.index'))

    # GET 방식일 때
    return render_template('items/write.html', categories = categories)


# 상품 상세페이지 (4월22일 수정함)
@bp.route('/product-details/<int:item_id>')
def product_details(item_id):
    # DB에서 해당 ID의 상품 하나 가져옴
    product = Item.query.get_or_404(item_id)
    cat = Category.query.get(product.category_id)
    status_list = ItemStatus.query.all()
    is_wished = False
    if g.user:
        # Favorite 모델에서 현재 유저와 상품 ID가 매칭되는 데이터가 있는지 확인
        f = Favorite.query.filter_by(user_id=g.user.id, item_id=item_id).first()
        if f:
            is_wished = True
    # 현재 상품(item_id)을 찜한 모든 데이터의 개수를 DB에서 직접 셉니다.
    wish_count = Favorite.query.filter_by(item_id=item_id).count()
    product_list = Item.query.filter(
        Item.user_id == product.user_id,
        Item.id != item_id,
        Item.is_deleted == False  # 삭제되지 않은 상품만
    ).order_by(Item.created_at.desc()).limit(6).all()

    return render_template('items/PDP.html', product = product, cat = cat, status_list=status_list, product_list=product_list,is_wished=is_wished,wish_count=wish_count)


# --- 찜하기 토글 (추가/해제) 기능 4월22일 ---
@bp.route('/wishlist/toggle/<int:item_id>')
@login_required
def toggle_favorite(item_id):
    item = Item.query.get_or_404(item_id)
    # 이미 찜했는지 확인
    f = Favorite.query.filter_by(user_id=g.user.id, item_id=item_id).first()

    if f:
        # 이미 있다면 삭제 (찜 해제)
        db.session.delete(f)
        db.session.commit()
        flash("찜 목록에서 제거되었습니다.")
    else:
        # 없다면 추가 (찜 등록)
        new_f = Favorite(user_id=g.user.id, item_id=item_id)
        db.session.add(new_f)
        db.session.commit()
        flash("찜 목록에 추가되었습니다!")

    return redirect(url_for('items.product_details', item_id=item_id))


# --- 마이페이지용 찜 삭제 기능 (창환 님이 에러 났던 부분) ---
@bp.route('/wishlist/delete/<int:item_id>', methods=['POST'])
@login_required
def remove_favorite(item_id):
    f = Favorite.query.filter_by(user_id=g.user.id, item_id=item_id).first()
    if f:
        db.session.delete(f)
        db.session.commit()
        flash("찜 목록에서 삭제되었습니다.")

    # 삭제 후 다시 찜목록으로 계속 유지 4월23일 2차수정
    return redirect(url_for('personal.my_page', tab='wish'))

# PDP.html 상품 상태 게시글 업로드 유저만 수정 가능하고 이외의 유저는 수정 불가능 함수 4월21일 수정
@bp.route('/modify-status/<int:item_id>', methods=['POST'])
@login_required
def modify_status(item_id):
    product = Item.query.get_or_404(item_id)

    # 판매자가 아닐 경우 수정 불가능
    if g.user != product.seller:
        return redirect(url_for('items.product_details', item_id=item_id))

    new_status = request.form.get('status_id', type=int)

    if not new_status:
        flash('변경할 상품 상태를 찾을 수 없습니다.')
        return redirect(url_for('items.product_details', item_id=item_id))

    existing_deal = Deal.query.filter_by(item_id=product.id).first()

    # 이미 거래가 등록된 상품은 상태변경 불가 4월22일
    if existing_deal:
        flash('거래가 등록된 상품은 상태를 다시 변경할 수 없습니다.')
        return redirect(url_for('items.product_details', item_id=item_id))

    # 판매완료(3)로 변경하려는 경우에는 바로 저장하지 않고 구매자 입력 페이지로 이동 거래상대저장 로직으로 역활중복이 생겨서 수정 4월22일
    if new_status == 3:
        return redirect(url_for('items.complete_deal', item_id=item_id))

    # 판매중 / 예약중은 기존처럼 바로 변경
    product.status_id = new_status
    db.session.commit()
    flash('상품 상태 수정 완료')

    return redirect(url_for('items.product_details', item_id=item_id))

# 거래상대 저장 4월21일 생성
@bp.route('/complete-deal/<int:item_id>/', methods=['GET', 'POST'])
@login_required
def complete_deal(item_id):
    product = Item.query.get_or_404(item_id)

    # 판매자만 접근 가능
    if g.user != product.seller:
        return redirect(url_for('items.product_details', item_id=item_id))

    # 이미 거래기록이 있으면 다시 등록하지 못하게 막기
    existing_deal = Deal.query.filter_by(item_id=product.id).first()
    if existing_deal:
        flash('이미 거래 정보가 등록된 상품입니다.')
        return redirect(url_for('items.product_details', item_id=item_id))

    if request.method == 'POST':
        buyer_nickname = request.form.get('buyer_nickname', '').strip()

        if not buyer_nickname:
            flash('구매자 닉네임을 입력해주세요.')
            return render_template('items/complete_deal.html', product=product)

        buyer = User.query.filter_by(nickname=buyer_nickname).first()

        if not buyer:
            flash('해당 닉네임의 사용자를 찾을 수 없습니다.')
            return render_template('items/complete_deal.html', product=product)

        if buyer.id == g.user.id:
            flash('본인은 구매자로 등록할 수 없습니다.')
            return render_template('items/complete_deal.html', product=product)

        new_deal = Deal(
            item_id=product.id,
            seller_id=product.user_id,
            buyer_id=buyer.id,
            deal_price=product.item_price,
            deal_status='completed',
            deal_datetime=datetime.now()
        )

        db.session.add(new_deal)
        product.status_id = 3   # 판매완료
        db.session.commit()

        flash('등록이 완료되었습니다.')
        return redirect(url_for('items.product_details', item_id=item_id))

    return render_template('items/complete_deal.html', product=product)

# 카테고리별 페이지
@bp.route('/product-categories/<int:category_id>')
def product_categories(category_id):

    cat = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    # 판매중 기준 우선 및 최신순 정렬
    category_items = Item.query.filter_by(category_id=category_id, is_deleted=False) \
        .order_by(Item.status_id.asc(), Item.created_at.desc()) \
        .paginate(page=page, per_page=20)

    all_categories = Category.query.all()

    return render_template('items/CP.html',
                           category_id = category_id, title = cat.category_name, product_list = category_items, all_categories=all_categories)

# 필터링 (거래 가능한 상품만 보기) 페이지
@bp.route('/product-status/<int:item_status_id>')
def product_statuses(item_status_id):
    page = request.args.get('page', 1, type=int)
    items = Item.query.filter_by(status_id=item_status_id, is_deleted=False) \
        .order_by(Item.created_at.desc()) \
        .paginate(page=page, per_page=20)

    all_categories = Category.query.all()

    return render_template('items/CP.html',
                           item_status_id = item_status_id, title = "거래 가능 상품", product_list=items, all_categories=all_categories)


# 4월24일 코드수정
@bp.route('/comment/create/<int:item_id>', methods=('POST',))
@login_required
def comment_create(item_id):
    product = Item.query.get_or_404(item_id)
    content = request.form.get('content')
    # 비밀글 체크박스 값 가져오기 (체크되면 'on'으로 들어옴)
    is_private = True if request.form.get('is_private') else False

    if content:
        comment = Comment(
            content=content,
            create_date=datetime.now(),
            items=product,
            user=g.user,
            is_private = is_private  # 비밀글 여부 저장
        )

        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('items.product_details', item_id=item_id))


# --- 판매자 답변 등록 (4월 24일 추가) ---
@bp.route('/reply/create/<int:comment_id>', methods=('POST',))
@login_required
def reply_create(comment_id):
    # 1. 답변을 달 부모 댓글을 가져옴
    parent_comment = Comment.query.get_or_404(comment_id)

    # 2. 보안 체크: 이 상품의 판매자만 답변을 달 수 있음
    if g.user != parent_comment.items.seller:
        flash('판매자만 답변을 등록할 수 있습니다.')
        return redirect(url_for('items.product_details', item_id=parent_comment.item_id))

    content = request.form.get('content')
    if content:
        reply = Comment(
            content=content,
            create_date=datetime.now(),
            item_id=parent_comment.item_id,  # 질문과 같은 상품 연결
            user=g.user,  # 답변자 (판매자)
            parent_id=comment_id,  # [핵심] 부모 댓글 ID 연결
            is_private=parent_comment.is_private  # 질문이 비밀글이면 답변도 비밀글로 설정
        )
        db.session.add(reply)
        db.session.commit()
        flash('답변이 등록되었습니다.')
    else:
        flash('답변 내용을 입력해주세요.')

    return redirect(url_for('items.product_details', item_id=parent_comment.item_id))


@bp.route('/comment/delete/<int:comment_id>')
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if g.user != comment.user:
        return redirect(url_for('items.product_details', item_id=comment.items.id))

    product_id = comment.items.id

    db.session.delete(comment)
    db.session.commit()

    # 이제 comment.item.id 대신 미리 뽑아둔 item_id를 사용합니다.
    return redirect(url_for('items.product_details', item_id=product_id))

@bp.route('/product/modify/<int:item_id>', methods=('GET', 'POST'))
@login_required
def product_modify(item_id):
    # 수정할 상품 데이터를 DB에서 가져오기
    product = Item.query.get_or_404(item_id)
    categories = Category.query.all()

    # 권한 확인
    if g.user.id != product.user_id:
        flash("수정 권한이 없습니다.", "error")
        return redirect(url_for('items.product_details', item_id=item_id))

    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        category_id = request.form.get('category')
        price = request.form.get('price', '')

        price_error = None

        try:
            clean_price = str(price).replace(',', '').strip()
            item_price = int(clean_price) if clean_price else 0
            if item_price < 0:
                price_error = "음수는 입력 불가능합니다."
        except ValueError:
            item_price = 0
            price_error = "숫자만 입력해주세요."

        errors = []
        # 검증 (토스트 알림을 위해 각 조건마다 flash 메시지 추가)
        if not title.strip():
            errors.append("상품명")
            flash("상품명을 입력해주세요.")

        if not category_id:
            errors.append("카테고리")
            flash("카테고리를 선택해주세요.")

        if not price.strip() or price_error:
            errors.append("가격")
            if price_error:
                flash(price_error)  # "음수는 입력 불가능합니다." 출력
            else:
                flash("가격을 입력해주세요.")

        if not content.strip():
            errors.append("상세 설명")
            flash("상세 설명을 입력해주세요.")

        # 에러가 하나라도 있으면 다시 작성 페이지로 (값 유지)
        if errors:
            return render_template('items/write.html',
                                   product=product,
                                   categories=categories,
                                   title=title,
                                   price=price,
                                   content=content,
                                   category_id=int(category_id) if category_id else None,
                                   errors=errors)

        old_title = product.item_title
        if old_title != title:
            user_base_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', g.user.nickname)

            if os.path.exists(user_base_path):
                # 유저 폴더 안을 뒤져서 '기존상품명_타임스탬프'로 된 폴더를 찾아냄
                for folder in os.listdir(user_base_path):
                    if folder.startswith(f"{old_title}_"):
                        old_folder_path = os.path.join(user_base_path, folder)
                        # 폴더명에서 상품명 부분만 새 이름으로 교체 (타임스탬프는 유지)
                        new_folder_name = folder.replace(old_title, title, 1)
                        new_folder_path = os.path.join(user_base_path, new_folder_name)

                        # 물리적 폴더 이름 변경 (이사 보내기)
                        if not os.path.exists(new_folder_path):
                            os.rename(old_folder_path, new_folder_path)

                        for img in product.images:
                            img.image_url = img.image_url.replace(f"/{folder}/", f"/{new_folder_name}/")

        # 닉네임 변경 시 기존 이미지 경로 이사 예외처리
        for img in product.images:
            if f'/static/uploads/products/{g.user.nickname}/' not in img.image_url:
                # 0423 수정: /static/uploads/products/옛날닉네임/상품명/... (프로필처럼 아이템폴더 새로 생성)
                path_parts = img.image_url.split('/')
                if len(path_parts) > 4:
                    old_nickname = path_parts[4]
                    img.image_url = img.image_url.replace(f'/products/{old_nickname}/', f'/products/{g.user.nickname}/')

        product.item_title = title
        product.item_description = content
        product.category_id = int(category_id)
        product.item_price = int(str(price).replace(',', '').strip())

        # 새 이미지 업로드 처리 (새 이미지를 새로 추가했을 때 작동)
        if 'images' in request.files:
            files = request.files.getlist('images')

            # 파일이 실제로 업로드 되었을 때만 폴더 생성 및 DB 등록
            if any(file and file.filename != '' for file in files):
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                folder_name = f"{title}_{timestamp}"

                # 현재 닉네임과 수정된 상품명으로 폴더 경로 설정
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', f'{g.user.nickname}', folder_name)
                os.makedirs(upload_path, exist_ok=True)

                for file in files:
                    if file and file.filename:
                        filename = file.filename
                        file.save(os.path.join(upload_path, filename))

                        # DB에 새 이미지 정보 추가 - 기존 것은 유지하고 새 이미지 추가만
                        web_path = f'/static/uploads/products/{g.user.nickname}/{folder_name}/{filename}'
                        new_img = ItemImage(item_id=product.id, image_url=web_path)
                        db.session.add(new_img)

        db.session.commit()
        flash("수정이 완료되었습니다!", "success")
        return redirect(url_for('items.product_details', item_id=item_id))

    return render_template('items/write.html', product=product, categories=categories)


@bp.route('/product/delete/<int:item_id>')
@login_required
def product_delete(item_id):
    item = Item.query.get_or_404(item_id)

    # 보안 체크: 로그인한 사람과 게시글 작성자가 같은지 확인
    if g.user != item.seller:
        # 본인이 아니면 상세 페이지로 다시 돌려보내기
        return redirect(url_for('items.product_details', item_id=item_id))

    item.is_deleted = True
    db.session.commit()
    flash('상품이 삭제되었습니다.')

    # 삭제 후에는 메인 페이지로 이동합니다.
    return redirect(url_for('main.index'))


@bp.route('/user/items/<int:user_id>/')
def user_items(user_id):
    item_list = Item.query.filter_by(user_id=user_id).order_by(Item.created_at.desc()).all()
    return redirect(url_for('personal.seller_profile', user_id=user_id))

