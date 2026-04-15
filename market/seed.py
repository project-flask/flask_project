from market import db, create_app
from market.models import Category, ItemStatus

def seed_data():
    app = create_app()
    with app.app_context():

        Category.query.delete()
        ItemStatus.query.delete()

        # 카테고리 리스트에 들어간 순서대로 ( 1 ~ 21 )
        categories = [
            "디지털기기", "생활가전", "가구/인테리어", "생활/주방", "유아동",
            "유아도서", "여성의류", "여성잡화", "남성패션/잡화", "뷰티/미용",
            "스포츠/레저", "취미/게임/음반", "도서", "티켓/교환권", "e쿠폰",
            "가공식품", "건강기능식품", "반려동물용품", "식물", "기타 중고물품",
            "삽니다"
        ]
        for name in categories:
            if not Category.query.filter_by(category_name=name).first():
                db.session.add(Category(category_name=name))

        # 상품 상태 리스트 ( 1 ~ 3 )
        statuses = ["판매중", "예약중", "판매완료"]
        for status_name in statuses:
            if not ItemStatus.query.filter_by(item_status=status_name).first():
                db.session.add(ItemStatus(item_status=status_name))

        db.session.commit()

if __name__ == "__main__":
    seed_data()