from market import create_app, db
from market.models import Item
from datetime import datetime

app = create_app()

# 핵심: 이 안에서 실행해야 'Application Context' 에러가 안 납니다!
with app.app_context():
    items = [
        Item(id='1', item_title='중고 아이폰 15', item_price='850,000', item_description='안녕하세요 아이폰 상태는 아주 깨끗합니다. 케이스 같이 드려요.',
             item_reg_datetime=datetime.now()),
        Item(id='2', item_title='에어팟 프로 2세대', item_price='210,000', item_description='쓴지 1주일 됬고 노이즈 캔슬링 잘 됩니다. 풀박스 구성.',
             item_reg_datetime=datetime.now()),
        Item(id='3', item_title='이케아 수납장', item_price='45,000', item_description='조립 완료된 상태입니다. 직접 가져가셔야 해요.',
             item_reg_datetime=datetime.now()),
        Item(id='4', item_title='캠핑용 텐트 (4인용)',item_price='120,000', item_description='작년에 구매해서 3번 사용했습니다. 상태 좋아요.',
              item_reg_datetime=datetime.now()),
        Item(id='5', item_title='닌텐도 스위치 OLED',item_price='320,000', item_description='액정 보호 필름 붙어있습니다. 조이콘 쏠림 없어요.',
              item_reg_datetime=datetime.now()),
        Item(id='6', item_title='독서대 (나무재질)',item_price='10,000', item_description='공부할 때 쓰기 좋습니다. 튼튼해요.',
             item_reg_datetime=datetime.now()),
        Item(id='7', item_title='미개봉 갤럭시 버즈3',item_price='150,000', item_description='사은품으로 받았는데 안 써서 팝니다. 새제품!',
             item_reg_datetime=datetime.now()),
        Item(id='8', item_title='자전거 헬멧',item_price='25,000', item_description='안전을 위해 구매했는데 사이즈가 안 맞아서 내놓습니다.',
             item_reg_datetime=datetime.now()),
        Item(id='9', item_title='가죽 쇼파 (3인용)',item_price='200,000', item_description='이사 때문에 급하게 처분합니다. 가죽 관리 잘 됨.',
              item_reg_datetime=datetime.now()),
        Item(id='10', item_title='나이키 운동화 270',item_price='60,000', item_description='실착 5회 미만입니다. 깨끗하게 세탁 완료.',
             item_reg_datetime=datetime.now()),
    ]

    # DB에 하나씩 추가
    for item in items:
        db.session.add(item)

    # 최종 저장
    db.session.commit()
    print("성공적으로 10개의 데이터가 DB에 저장되었습니다!")