import os

from flask import Blueprint, render_template, request, url_for, redirect, g, flash, current_app
from market.views.auth_view import login_required
from market import db
from market.models import User, Item, Category, Comment, ItemStatus, ItemImage, Deal
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

    if request.method == 'POST':
        title = request.form.get('title')
        price = request.form.get('price')
        content = request.form.get('content')
        category_id = request.form.get('category')
        status_id = request.form.get('status')

        # 가격 예외처리
        try:
            clean_price = str(price).replace(',', '').strip()
            item_price = int(clean_price) if clean_price else 0
        except ValueError:
            item_price = 0  # 숫자가 아니면 그냥 0원 처리

        # 카테고리 예외처리
        try:
            cat_id = int(category_id) if category_id else 20  # 기본값 기타
        except ValueError:
            cat_id = 20

        # 상품 상태 예외처리
        try:
            st_id = int(status_id) if status_id else 1      # 기본값 판매중
        except ValueError:
            st_id = 1

        # DB에 저장할 객체 만들기
        if title:
            new_item = Item(
                item_title = title,
                item_price = item_price,
                item_description = content,
                user_id = g.user.id,
                category_id = cat_id,
                status_id = 1  # seed.py의 '판매중'을 기본 default 1번으로 가져옴
            )

            db.session.add(new_item)
            # db에 미리 전달 후 new_item.id 확보
            db.session.flush()

            if 'images' in request.files:
                files = request.files.getlist('images')

                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', f'user_{g.user.id}', f'item_{new_item.id}')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                for file in files:
                    if file and file.filename:
                        # 파일 이름 보안 처리
                        filename = secure_filename(file.filename)
                        # 실제 서버 폴더에 저장
                        file.save(os.path.join(upload_path, filename))

                        # DB에 이미지 경로 기록 (ItemImage 모델 활용 4월17일 수정함)
                        web_path = f'/static/uploads/user_{g.user.id}/item_{new_item.id}/{filename}'
                        new_img = ItemImage(item_id=new_item.id, image_url=web_path)
                        db.session.add(new_img)

            db.session.commit()

            # 등록 완료 후 메인으로 전달
            return redirect(url_for('main.index'))

    # GET 방식일 때
    categories = Category.query.all()
    return render_template('items/write.html', categories = categories)


# 상품 상세페이지 (4월17일 product_list 추가함)
@bp.route('/product-details/<int:item_id>')
def product_details(item_id):
    # DB에서 해당 ID의 상품 하나 가져옴
    product = Item.query.get_or_404(item_id)
    cat = Category.query.get(product.category_id)
    status_list = ItemStatus.query.all()
    product_list = Item.query.filter(
        Item.user_id == product.user_id,
        Item.id != item_id,
        Item.is_deleted == False  # 삭제되지 않은 상품만
    ).order_by(Item.created_at.desc()).limit(6).all()

    return render_template('items/PDP.html', product = product, cat = cat, status_list=status_list, product_list=product_list)

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

    # 판매완료(3)로 변경하려는 경우에는 바로 저장하지 않고 구매자 입력 페이지로 이동
    if new_status == 3:
        existing_deal = Deal.query.filter_by(item_id=product.id).first()

        # 이미 판매완료 처리와 거래 등록이 끝난 상품이면 다시 입력 페이지로 보내지 않음
        if product.status_id == 3 and existing_deal:
            flash('이미 판매완료 처리된 상품입니다.')
            return redirect(url_for('items.product_details', item_id=item_id))

        return redirect(url_for('items.complete_deal', item_id=item_id))

    existing_deal = Deal.query.filter_by(item_id=product.id).first()

    # 이미 거래가 등록된 상품은 판매완료 외 다른 상태로 되돌릴 수 없음
    if existing_deal:
        flash('거래가 등록된 상품은 상태를 다시 변경할 수 없습니다.')
        return redirect(url_for('items.product_details', item_id=item_id))

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

        flash('거래 정보가 등록되었고 상품이 판매완료로 변경되었습니다.')
        return redirect(url_for('items.product_details', item_id=item_id))

    return render_template('items/complete_deal.html', product=product)

# 카테고리별 페이지
@bp.route('/product-categories/<int:category_id>')
def product_categories(category_id):

    cat = Category.query.get_or_404(category_id)
    # 판매중 기준 우선 및 최신순 정렬
    category_items = Item.query.filter_by(category_id=category_id, is_deleted=False)\
                    .order_by(Item.status_id.asc(), Item.created_at.desc()).all()

    all_categories = Category.query.all()

    return render_template('items/CP.html',
                           category_id = category_id, title = cat.category_name, product_list = category_items, all_categories=all_categories)

# 필터링 (거래 가능한 상품만 보기) 페이지
@bp.route('/product-status/<int:item_status_id>')
def product_statuses(item_status_id):
    items = Item.query.filter_by(status_id=item_status_id, is_deleted=False)\
            .order_by(Item.created_at.desc()).all()

    all_categories = Category.query.all()

    return render_template('items/CP.html',
                           item_status_id = item_status_id, title = "거래 가능 상품", product_list=items, all_categories=all_categories)


@bp.route('/comment/create/<int:item_id>', methods=('POST',))
@login_required
def comment_create(item_id):
    product = Item.query.get_or_404(item_id)
    content = request.form.get('content')

    if content:
        comment = Comment(
            content=content,
            create_date=datetime.now(),
            items=product,
            user=g.user
        )

        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('items.product_details', item_id=item_id))


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
    # 1. 수정할 상품 데이터를 DB에서 가져오기
    product = Item.query.get_or_404(item_id)

    # 2. 권한 확인
    if g.user.id != product.user_id:
        return redirect(url_for('items.product_details', item_id=item_id))

    if request.method == 'POST':
        product.item_title = request.form.get('title')  # 'subject'를 'title'로 변경
        product.item_description = request.form.get('content')
        product.category_id = request.form.get('category')

        # 가격 처리
        price = request.form.get('price')
        clean_price = str(price).replace(',', '').strip()
        product.item_price = int(clean_price) if clean_price else 0

        db.session.commit()
        return redirect(url_for('items.product_details', item_id=item_id))

    else:
        categories = Category.query.all()
        return render_template('items/write.html', product=product, categories=categories)


@bp.route('/product/delete/<int:item_id>')
@login_required
def product_delete(item_id):
    item = Item.query.get_or_404(item_id)

    # 보안 체크: 로그인한 사람과 게시글 작성자가 같은지 확인
    if g.user != item.seller:
        # 본인이 아니면 상세 페이지로 다시 돌려보내기
        return redirect(url_for('items.product_details', item_id=item_id))

    db.session.delete(item)
    db.session.commit()

    # 삭제 후에는 메인 페이지로 이동합니다.
    return redirect(url_for('main.index'))


@bp.route('/user/items/<int:user_id>/')
def user_items(user_id):
    item_list = Item.query.filter_by(user_id=user_id).order_by(Item.created_at.desc()).all()
    return redirect(url_for('personal.seller_profile', user_id=user_id))

