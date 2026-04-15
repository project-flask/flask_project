
from flask import Blueprint, render_template, request, url_for, redirect, g
from market.views.auth_view import login_required
from market import db
from market.models import Item, Category, Comment

from datetime import datetime  # 날짜 기능을 쓰기 위해 추가



bp = Blueprint('items', __name__, url_prefix='/items')

# 글쓰기
@bp.route('/product-upload/', methods=['GET', 'POST'])
@login_required
def product_upload():

    if request.method == 'POST':
        # HTML 폼에서 보낸 데이터 읽어옴
        title = request.form.get('subject')
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
            cat_id = int(category_id) if category_id else 21  # 기본값 기타
        except ValueError:
            cat_id = 21

        # 상품 상태 예외처리
        try:
            st_id = int(status_id) if status_id else 3
        except ValueError:
            st_id = 3

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
    item = Item.query.get_or_404(item_id)
    item_list = Item.query.order_by(Item.created_at.desc()).limit(6).all()
    return render_template('items/PDP.html', item = item,item_list=item_list)

# 카테고리별 페이지
@bp.route('/product-categories/<int:category_id>')
def product_categories(category_id):
    cat = Category.query.get_or_404(category_id)
    # DB에서 해당 카테고리 상품만 필터링해서 가져옴
    category_items = Item.query.filter_by(category_id=category_id).all()
    return render_template('items/CP.html', category_id = category_id, title = cat.category_name, items = category_items)

# 필터링 (거래 가능한 상품만 보기) 페이지
@bp.route('/product-status/<int:item_status_id>')
def product_statuses(item_status_id):
    item_statuses = Item.query.filter_by(status_id=item_status_id).all()
    return render_template('items/CP.html', items = item_statuses, title = "거래 가능 상품")


@bp.route('/comment/create/<int:item_id>', methods=('POST',))
@login_required
def comment_create(item_id):
    item = Item.query.get_or_404(item_id)
    content = request.form.get('content')

    if content:
        # 모델 설계도와 똑같이 'create_date'를 사용합니다.
        comment = Comment(
            content=content,
            create_date=datetime.now(),  # 확인하신 모델 변수명과 일치시켰습니다!
            item=item,
            user=g.user
        )
        db.session.add(comment)
        db.session.commit()

        print(f"--- 댓글 저장 성공: {content[:10]}... ---")

    return redirect(url_for('items.product_details', item_id=item_id))

# 서버에 삭제 함수 만들기 4월15일 만듬
@bp.route('/comment/delete/<int:comment_id>')
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if g.user != comment.user:
        return redirect(url_for('items.product_details', item_id=comment.item.id))

    # ★ 핵심: 삭제하기 전에 돌아갈 상품의 ID를 미리 변수에 저장해둡니다.
    item_id = comment.item.id

    db.session.delete(comment)
    db.session.commit()

    # 이제 comment.item.id 대신 미리 뽑아둔 item_id를 사용합니다.
    return redirect(url_for('items.product_details', item_id=item_id))

 # 서버에 게시글 삭제 함수 4월15일 만듬
@bp.route('/product/delete/<int:item_id>')
@login_required
def product_delete(item_id):
    item = Item.query.get_or_404(item_id)

    # 보안 체크: 로그인한 사람과 게시글 작성자가 같은지 확인
    if g.user != item.user:
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

