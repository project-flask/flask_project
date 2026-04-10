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
        #  중복 사용자 확인(id 기준)
        user = User.query.filter_by(id=form.username.data).first()
        if not user:
            user = User(
                id=form.user_id.data,  # 모델의 id 필드
                username=form.username.data,  # 모델의 username 필드
                password=generate_password_hash(form.password1.data),
                email=form.email.data,
                phone=form.phone.data  # 모델의 phone 필드
                )
            db.session.add(user)
            db.session.commit()
            # 가입 성공 후 메인 페이지로 이동
            return redirect(url_for('main_view.index'))
        else:
            flash('이미 존재하는 사용자입니다.')

    return render_template('auth/signup.html', form=form)

#로그인 라우팅 함수
@bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(id=form.username.data).first()
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

# 로그인 여부 확인
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
