from flask import Blueprint, redirect, url_for
from market.services.deal_service import change_deal_status

# 거래 관련 URL을 묶는 Blueprint
# → /deal 로 시작하는 모든 거래 기능 담당
bp = Blueprint('deal', __name__, url_prefix='/deal')


# 거래 완료 처리
# POST 요청만 허용 (DB 상태 변경은 GET 사용 금지)
@bp.route('/complete/<int:id>', methods=['POST'])
def complete_deal(id):

    try:
        # ✅ 서비스 레이어 호출
        # 거래 상태를 completed 로 변경
        # + 상품 상태 자동 변경 (판매완료)
        deal = change_deal_status(id, 'completed')

        # 존재하지 않는 거래일 경우
        if not deal:
            return "Deal not found", 404

    # 서비스 내부에서 발생한 예외 처리
    except Exception as e:
        # 로그 남기기
        return str(e), 400

    # 처리 완료 후 메인 페이지로 이동
    return redirect(url_for('main.index'))