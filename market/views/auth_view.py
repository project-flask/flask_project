import functools
import requests
from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from market import db
from market.models import User
from market.forms import UserCreateForm, UserLoginForm, FindAccountForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


# [일반 회원가입]
@bp.route('/signup/', methods=['GET', 'POST'])

# 일반 아이디 회원가입
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 아이디 중복 체크
        user = User.query.filter_by(login_id=form.user_id.data).first()
        if not user:

            new_user = User(
                login_id=form.user_id.data,
                username=form.username.data,
                nickname=form.nickname.data,
                password=generate_password_hash(form.password1.data),
                email=form.email.data,
                phone=form.phone.data
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            flash('이미 존재하는 아이디입니다.')
    return render_template('auth/signup.html', form=form)

# [일반 로그인]
@bp.route('/login/', methods=['GET', 'POST'])

# 일반 아이디 로그인
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(login_id=form.username.data).first()
        if not user:
            error = '존재하지 않는 사용자입니다.'
        elif not check_password_hash(user.password, form.password.data):
            error = '비밀번호가 올바르지 않습니다.'
        if error is None:
            session.clear()
            session['user_id'] = user.id

            return redirect(url_for('main.index'))

        flash(error)
    return render_template('auth/login.html', form=form)


@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


# 로그아웃 - 세션 정보를 모두 삭제
@bp.route('/logout/')
def logout():

    session.clear()
    return redirect(url_for('main.index'))


# [계정 찾기(아이디/비밀번호 통합)]
@bp.route('/find_account/', methods=['GET', 'POST'])
def find_account():
    form = FindAccountForm()

    if request.method == 'POST':
        # 아이디 찾기
        if 'username' in request.form and 'email' in request.form:
            user = User.query.filter_by(
                username=form.username.data,
                email=form.email.data
            ).first()
            if user:
                flash(f"찾으시는 아이디는 [{user.login_id}] 입니다.", "success")
            else:
                flash("일치하는 회원 정보가 없습니다.", "danger")

        # 비밀번호 찾기
        elif 'user_id' in request.form and 'email_for_pw' in request.form:
            user = User.query.filter_by(
                login_id=form.user_id.data,
                email=form.email_for_pw.data
            ).first()

            # 비밀번호 찾고 reset_password.html에서 그대로 확인
            if user:
                session['temp_reset_user_id'] = user.id
                return redirect(url_for('auth.reset_password'))
            else:
                flash("일치하는 회원 정보가 없습니다.", "danger")

    return render_template('auth/find_account.html', form=form)


# 카카오 로그인 설정값
CLIENT_ID = "e17055a5c7eb91012c7140978ae7788a"
CLIENT_SECRET = "pBLVBBvlQebKOiGfJxZWa0h9VxRPRcTu"
REDIRECT_URI = "http://localhost:5000/auth/kakao/callback/"
SIGNOUT_REDIRECT_URI = "http://127.0.0.1:5000/auth/logout/callback/"

# 카카오 서버와 직접 통신하는 클래스
class Oauth:
    def __init__(self):
        self.auth_server = "https://kauth.kakao.com%s"
        self.api_server = "https://kapi.kakao.com%s"
        self.default_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

   # 유저의 프로필 정보 요청
    def auth(self, code):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        ).json()

    def userinfo(self, bearer_token):
        return requests.get(
            url=self.api_server % "/v2/user/me",
            headers={**self.default_header, **{"Authorization": bearer_token}}
        ).json()

# 카카오 로그인 라우팅
@bp.route('/kakao/')
def kakao_sign_in():
    kakao_oauth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&prompt=login"
    return redirect(kakao_oauth_url)


# 카카오 콜백 함수
@bp.route('/kakao/callback/')
def callback():
    # 1. 카카오로부터 전달받은 인증 코드 확인
    code = request.args.get("code")
    if not code:
        return redirect(url_for('auth.login'))

    # 2. 인증 코드로 카카오 토큰 요청
    oauth = Oauth()
    auth_info = oauth.auth(code)

    if "error" in auth_info:
        flash(f"인증 실패: {auth_info.get('error_description')}")
        return redirect(url_for('auth.login'))

    # 3. 토큰을 이용해 실제 사용자 정보 요청
    user_data = oauth.userinfo("Bearer " + auth_info['access_token'])

    if not user_data or "id" not in user_data:
        flash("카카오 정보를 불러오지 못했습니다.")
        return redirect(url_for('auth.login'))

    # --- [데이터 추출 및 가공] ---
    kakao_id = str(user_data.get('id'))  # 카카오 고유번호 (login_id로 사용)
    kakao_account = user_data.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    # 닉네임: 카카오 닉네임을 가져옴. 없으면 ID 기반으로 생성
    nickname = profile.get("nickname")
    if not nickname:
        nickname = f"카카오유저_{kakao_id[:5]}"

    # 이름: 닉네임과 동일하게 설정
    username = profile.get("nickname", "카카오유저")

    # 이메일: 이메일이 없는 경우 랜덤 이메일 생성
    email = kakao_account.get("email") or f"{kakao_id}@kakao.com"

    # --- [DB 연동 및 가입 처리] ---
    # 이미 가입된 카카오 유저인지 login_id로 확인
    user = User.query.filter_by(login_id=kakao_id).first()

    if not user:
        # 처음 온 유저라면 새 유저 객체 생성
        user = User(
            login_id=kakao_id,
            username=username,
            nickname=nickname,
            email=email,
            password=generate_password_hash(kakao_id),
            phone=None
        )
        db.session.add(user)
        db.session.commit()

    # 4. 세션 처리 및 로그인 완료
    session.clear()
    session['user_id'] = user.id
    session['is_kakao'] = True

    return redirect(url_for('main.index'))


# [비밀번호 재설정]
@bp.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    # 세션에 정보 없으면 플래시 메시지
    user_id = session.get('temp_reset_user_id')
    if not user_id:
        flash("정상적인 접근이 아닙니다.", "danger")
        return redirect(url_for('auth.find_account'))

    from market.forms import PasswordResetForm
    form = PasswordResetForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.get(user_id)
        if user:
            # 새 비밀번호 암호화해서 저장
            user.password = generate_password_hash(form.password.data)
            db.session.commit()

            # 비번 변경 후
            session.pop('temp_reset_user_id', None)
            flash("비밀번호가 변경되었습니다.<br>새 비밀번호로 로그인하세요.", "success")
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


# 데코레이션 함수
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''

            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)

    return wrapped_view


