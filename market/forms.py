from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email


# 회원가입
class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)]) # 사용자 이름(아이디)
    password1 = PasswordField('비밀번호', validators=[DataRequired(), EqualTo('password2', message='비밀번호가 일치하지 않습니다.')]) # 비밀번호
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()]) # 비밀번호 확인
    email = EmailField('이메일', validators=[DataRequired(), Email()]) # 이메일