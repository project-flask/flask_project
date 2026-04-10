from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/')
@login_required
def mypage():
    return render_template(
        'mypage.html',
        user=current_user
    )