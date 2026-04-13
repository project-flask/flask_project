from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from market import db
from market.forms import UserCreateForm, UserLoginForm
from market.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

#회원가입 라우팅 함수
@bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():

        # login_id로 중복 체크
        user = User.query.filter_by(login_id=form.user_id.data).first()

        if not user:
            new_user = User(
                login_id=form.user_id.data,  # 유저가 입력한 ID ('test00' 등)
                username=form.username.data,
                password=generate_password_hash(form.password1.data),
                email=form.email.data,
                phone=form.phone.data
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))  # 가입 후 로그인 페이지로
        else:
            flash('이미 존재하는 아이디입니다.')

    return render_template('auth/signup.html', form=form)

#로그인 라우팅 함수
@bp.route('/login/', methods=['GET', 'POST'])
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

            return redirect(url_for('main_view.index'))

        flash(error)
    return render_template('auth/login.html', form=form)

# 로그인 여부 확인
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
        
# 로그아웃 라우팅 함수
@bp.route('/logout/')
def logout():
    session.clear() # 세션의 모든 정보(user_id 등) 삭제
    return redirect(url_for('main_view.index')) # 로그아웃 후 메인 페이지로 이동

# 계정찾기 라우팅 함수
@bp.route('/find_account/', methods=['GET', 'POST'])
def find_account():
    if request.method == 'POST':
        # 1. 폼에서 입력한 이름과 이메일 가져오기
        input_name = request.form.get('username')
        input_email = request.form.get('email')

        # 2. DB에서 일치하는 유저 찾기
        user = User.query.filter_by(username=input_name, email=input_email).first()

        if user:
            # 아이디(login_id)를 찾았을 때
            flash(f"찾으시는 아이디는 [{user.login_id}] 입니다.", "success")
        else:
            # 일치하는 정보가 없을 때
            flash("일치하는 회원 정보가 없습니다.", "danger")

    return render_template('auth/find_account.html')