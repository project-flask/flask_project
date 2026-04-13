import os

BASE_DIR = os.path.dirname(__file__)

# DB접속 주소
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'market.db'))

# 이벤트 처리
SQLALCHEMY_TRACK_MODIFICATIONS = False


# CSRF 토큰 생성 (CSRF 공격의 방어를 위해 생성하는 무작위 문자열)
# 실제 운영 때는 dev같은 간단한 문자열 사용하면 위험함
SECRET_KEY = 'dev'