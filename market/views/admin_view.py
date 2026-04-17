from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from market import db
from ..models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 관리자 아니면 못 들어오게 하는 기능
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# 관리자 페이지 (검색 & 리스트)
@admin_bp.route('/')
@login_required
@admin_required
def index():
    search = request.args.get('search', '')
    if search:
        users = User.query.filter(User.nickname.contains(search)).all()
    else:
        users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template('personal/adminpage.html', users=users, search=search)

# 회원 강제 탈퇴 (버튼 누르면 실행)
@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"{user.nickname}님을 탈퇴 처리했습니다.")
    return redirect(url_for('admin.index'))