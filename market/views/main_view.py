from flask import Blueprint, redirect, url_for, render_template

bp = Blueprint('main_view', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('main.html')

@bp.route('/detail')
def detail():
    return render_template('detail.html', product=None)

@bp.route('/signup')
def signup():
    return render_template('auth/signup.html')