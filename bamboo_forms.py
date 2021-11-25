from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.fields.html5 import TimeField, DateField
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
                            render_kw={'placeholder': 'Фамилия',
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


class Createform(FlaskForm):
    title_create = StringField("Заголовок", validators=[DataRequired(), Length(min=1, max=59)],
                               render_kw={'placeholder': 'Заголовок',
                                          'autocomplete': 'off'})

    description_create = TextAreaField("Описание",
                                       render_kw={'placeholder': 'Описание',
                                                  'autocomplete': 'off',
                                                  'rows': '10', 'cols': '33'})

    date_create = DateField("Выберите день", validators=[DataRequired()])

    time_create = TimeField("Выберите время", validators=[DataRequired()])

    submit_create = SubmitField("Создать",
                                render_kw={})


class Editform(FlaskForm):
    email_edit = StringField("Введите почту: ", validators=[Email(), DataRequired()])

    submit_edit = SubmitField("Добавить в конференцию")
