from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email


# 회원가입 폼
class UserCreateForm(FlaskForm):
    user_id = StringField('아이디', validators=[DataRequired(message='아이디를 입력해주세요.'),
        Length(min=3, max=20, message='아이디는 3~20자여야 합니다.')
    ])
    username = StringField('사용자이름', validators=[
        DataRequired(message='이름을 입력해주세요.'),
        Length(min=3, max=25, message='이름은 3~25자여야 합니다.')
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

# 로그인 폼
class UserLoginForm(FlaskForm):
    username = StringField('아이디', validators=[
        DataRequired(message='아이디를 입력해주세요.')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력해주세요.')
    ])
