from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class Loginform(FlaskForm):
    email_login = StringField("Почта", validators=[Email(), DataRequired(), Length(min=2, max=40)],
                              render_kw={'placeholder': 'E-mail',
                                         'autocomplete': 'off'})

    psw_login = PasswordField("Пароль", validators=[DataRequired(), Length(min=6, max=100)],
                              render_kw={'placeholder': 'Пароль',
                                         'autocomplete': 'off',
                                         'id': 'password-input'})

    remember_login = BooleanField("Запомнить меня", default=False,
                                  render_kw={'id': 'remChk'})

    submit_login = SubmitField("Войти",
                               render_kw={'class': 'button button-block'})


class Registerform(FlaskForm):
    fname_reg = StringField("Имя", validators=[DataRequired(), Length(min=2, max=40)],
                            render_kw={'placeholder': 'Имя',
                                       'autocomplete': 'off'})

    lname_reg = StringField("Фамилия", validators=[DataRequired(), Length(min=2, max=40)],
                            render_kw={'placeholder': 'Фалилия',
                                       'autocomplete': 'off'})

    email_reg = StringField("Почта", validators=[Email(), DataRequired(), Length(min=2, max=40)],
                            render_kw={'placeholder': 'E-mail',
                                       'autocomplete': 'off'})

    psw_reg = PasswordField("Пароль", validators=[DataRequired(), Length(min=6, max=100)],
                            render_kw={'placeholder': 'Пароль',
                                       'autocomplete': 'off'})

    psw2_reg = PasswordField("Повтор пароля", validators=[DataRequired(), EqualTo('psw_reg')],
                             render_kw={'placeholder': 'Повторите пароль',
                                        'autocomplete': 'off'})

    submit_reg = SubmitField("Зарегистрироваться",
                             render_kw={'class': 'button button-block'})
