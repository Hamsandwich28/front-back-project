from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=2, max=50)])
    email = StringField("Электронная почта: ", validators=[Email()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=6, max=60)])
    psw2 = PasswordField("Повторите пароль: ", validators=[DataRequired(), EqualTo('psw')])
    remember = BooleanField("Запомнить ")
    submit = SubmitField("Зарегистрироваться ")
