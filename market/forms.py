from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from market.models import User


# 회원가입 폼
class UserCreateForm(FlaskForm):
    user_id = StringField('아이디', validators=[DataRequired(message='아이디를 입력해주세요.'),
        Length(min=3, max=20, message='아이디는 3~20자여야 합니다.')
    ])
    username = StringField('사용자이름', validators=[
        DataRequired(message='이름을 입력해주세요.'),
        Length(min=2, max=25, message='이름은 2~25자여야 합니다.')
    ])
    nickname = StringField('닉네임', validators=[
        DataRequired('닉네임은 필수입니다.'),
        Length(min=2, max=10, message='닉네임은 2~10자여야 합니다.')
    ])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력해주세요.'),
        EqualTo('password2', message='비밀번호가 일치하지 않습니다.')
    ])
    password2 = PasswordField('비밀번호확인', validators=[
        DataRequired(message='비밀번호를 한 번 더 입력해주세요.')
    ])
    email = EmailField('이메일', validators=[
        DataRequired(message='이메일을 입력해주세요.'),
        Email(message='유효한 이메일 형식이 아닙니다.')
    ])
    phone = StringField('전화번호', validators=[
        DataRequired(message='전화번호를 입력해주세요.')
    ])

    # --- 여기서부터 중복 체크 함수 ---
    # 아이디 중복 체크
    def validate_user_id(self, field):
        if User.query.filter_by(login_id=field.data).first():
            raise ValidationError('이미 사용 중인 아이디입니다.')

    # 닉네임 중복 체크
    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('이미 사용 중인 닉네임입니다.')


# 로그인 폼
class UserLoginForm(FlaskForm):
    username = StringField('아이디', validators=[
        DataRequired(message='아이디를 입력해주세요.')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력해주세요.')
    ])


# 계정찾기 폼
class FindAccountForm(FlaskForm):
    # 아이디 찾기용
    username = StringField('이름', validators=[DataRequired('이름을 입력해주세요.')])
    email = StringField('이메일', validators=[DataRequired('이메일을 입력해주세요.'), Email('이메일 형식이 아닙니다.')])
    # 비밀번호 찾기용
    user_id = StringField('아이디', validators=[DataRequired('아이디를 입력해주세요.')])
    email_for_pw = StringField('이메일', validators=[DataRequired('이메일을 입력해주세요.'), Email('이메일 형식이 아닙니다.')])


# 비밀번호 재설정 폼
class PasswordResetForm(FlaskForm):
    # 첫 번째 새 비밀번호 입력창
    password = PasswordField('새 비밀번호', validators=[
        DataRequired('새 비밀번호를 입력해주세요.'),
        EqualTo('confirm_password', message='비밀번호가 일치하지 않습니다.')
    ])
    # 비밀번호 확인 입력창
    confirm_password = PasswordField('비밀번호 확인', validators=[
        DataRequired('비밀번호 확인을 한 번 더 입력해주세요.')
    ])