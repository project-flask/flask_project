#import locale
from datetime import timedelta

# linux: ko_KR.UTF-8 / Windows: ko_KR ( 한글패치 )
# try:
#     locale.setlocale(locale.LC_ALL, 'ko_KR')
# except:
#     locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')

# 시간, 날짜 포매팅 함수
def format_datetime(value, fmt="%Y.%m.%d %p %I:%M"):
    if not value:
        return ""

    # UTC 강제 한국 시간 변환
    try:
        return (value + timedelta(hours=9)).strftime(fmt)
    except:
        return value.strftime(fmt)