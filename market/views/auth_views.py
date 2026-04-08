from flask import Blueprint, request, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash

from market import db
from market.forms import UserCreateForm
from market.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                        email=form.email.data)
            db.session.add(user)
            db.session.commit()
            # 가입 성공 후 메인 페이지로 이동
            return redirect(url_for('main_view.index')) 
        else:
            flash('이미 존재하는 사용자입니다.')
            
    return render_template('auth/signup.html', form=form)
