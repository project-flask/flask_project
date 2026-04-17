import os

from flask import Blueprint, render_template, request, url_for, redirect, g, flash, current_app
from market.views.auth_view import login_required
from market import db
from market.models import User, Item, Category, Comment, ItemStatus, ItemImage
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
        # HTML 폼에서 보낸 데이터 읽어옴
        title = request.form.get('title')
        price = request.form.get('price')
        content = request.form.get('content')
        category_id = request.form.get('category')
        status_id = request.form.get('status')

        # 가격 예외처리
        try:
            # 콤마(,)가 포함되어 있을 수도 있으니 제거하고 숫자로 변환
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

                        # DB에 이미지 경로 기록 (ItemImage 모델 활용)
                        web_path = f'/static/uploads/user_{g.user.id}/item_{new_item.id}/{filename}'
                        new_img = ItemImage(item_id=new_item.id, image_url=web_path)
                        db.session.add(new_img)

            db.session.commit()

            # 등록 완료 후 메인으로 전달
            return redirect(url_for('main.index'))

    # GET 방식일 때
    categories = Category.query.all()
    return render_template('items/write.html', categories = categories)

# 상품 상세페이지
@bp.route('/product-details/<int:item_id>')
def product_details(item_id):
    # DB에서 해당 ID의 상품 하나 가져옴
    product = Item.query.get_or_404(item_id)
    cat = Category.query.get(product.category_id)
    status_list = ItemStatus.query.all()
    return render_template('items/PDP.html', product = product, cat = cat, status_list=status_list)

# PDP.html 상품 상태 게시글 업로드 유저만 수정 가능하고 이외의 유저는 수정 불가능 함수
@bp.route('/modify-status/<int:item_id>', methods=['POST'])
@login_required
def modify_status(item_id):
    product = Item.query.get_or_404(item_id)

    # 판매자가 아닐 경우 수정 불가능
    if g.user != product.seller:
        return redirect(url_for('items.product_details', item_id=item_id))

    new_status = request.form.get('status_id')

    if new_status:
        product.status_id = int(new_status)
        db.session.commit()
        flash('상품 상태 수정 완료')

    return redirect(url_for('items.product_details', item_id=item_id))

# 카테고리별 페이지
@bp.route('/product-categories/<int:category_id>')
def product_categories(category_id):
    cat = Category.query.get_or_404(category_id)
    # DB에서 해당 카테고리 상품만 필터링해서 가져옴
    category_items = Item.query.filter_by(category_id=category_id).all()
    return render_template('items/CP.html', category_id = category_id, title = cat.category_name, product_list = category_items)

# 필터링 (거래 가능한 상품만 보기) 페이지
@bp.route('/product-status/<int:item_status_id>')
def product_statuses(item_status_id):
    item_statuses = Item.query.filter_by(status_id=item_status_id).all()
    return render_template('items/CP.html', items = item_statuses, title = "거래 가능 상품")


@bp.route('/comment/create/<int:item_id>', methods=('POST',))
@login_required
def comment_create(item_id):
    product = Item.query.get_or_404(item_id)
    content = request.form.get('content')

    if content:
        # 모델 설계도와 똑같이 'create_date'를 사용합니다.
        comment = Comment(
            content=content,
            create_date=datetime.now(),  # 확인하신 모델 변수명과 일치시켰습니다!
            item=product,
            user=g.user
        )
        db.session.add(comment)
        db.session.commit()

        print(f"--- 댓글 저장 성공: {content[:10]}... ---")

    return redirect(url_for('items.product_details', item_id=item_id, item=product))

# 서버에 삭제 함수 만들기 4월15일 만듬
@bp.route('/comment/delete/<int:comment_id>')
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if g.user != comment.user:
        return redirect(url_for('items.product_details', item_id=comment.item.id))

    # ★ 핵심: 삭제하기 전에 돌아갈 상품의 ID를 미리 변수에 저장해둡니다.
    product_id = comment.item.id

    db.session.delete(comment)
    db.session.commit()

    # 이제 comment.item.id 대신 미리 뽑아둔 item_id를 사용합니다.
    return redirect(url_for('items.product_details', item_id=product_id))



  # 4월16일 게시글 수정오늘 추가함
@bp.route('/product/modify/<int:item_id>', methods=('GET', 'POST'))
@login_required
def product_modify(item_id):
    # 1. 수정할 상품 데이터를 DB에서 가져오기
    product = Item.query.get_or_404(item_id)

    # 2. 권한 확인
    if g.user.id != product.user_id:
        return redirect(url_for('items.product_details', item_id=item_id))

    if request.method == 'POST':
        # 3. [중요] 창환 님의 product_upload 함수에서 쓰는 name 값들과 똑같이 맞춰야 합니다!
        product.item_title = request.form.get('subject')  # 'item_title' -> 'subject'로 수정
        product.item_description = request.form.get('content')  # 'item_description' -> 'content'로 수정
        product.category_id = request.form.get('category')  # 'category_id' -> 'category'로 수정

        # 가격 처리 (위의 upload 함수 로직 참고)
        price = request.form.get('price')
        clean_price = str(price).replace(',', '').strip()
        product.item_price = int(clean_price) if clean_price else 0

        db.session.commit()
        return redirect(url_for('items.product_details', item_id=item_id))

    else:
        # 4. [중요] 아까 사진에서 확인한 'items/write.html'로 경로를 바꿉니다!
        categories = Category.query.all()
        return render_template('items/write.html', product=product, categories=categories)

 # 서버에 게시글 삭제 함수 4월15일 만듬
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
    # Item.created_at으로 변경 완료!
    item_list = Item.query.filter_by(user_id=user_id).order_by(Item.created_at.desc()).all()
    return render_template('main.html', item_list=item_list)

