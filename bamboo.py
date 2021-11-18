# system import
import os
import psycopg2
import configparser
from flask import Flask, g, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# self import
from bamboo_forms import Loginform, Registerform
from bamboo_database_test import BDatabaseTest
from bamboo_userlogin import Userlogin, userify

# config
DEBUG = True
SECRET_KEY = 'kmgdtjnosfepplrgb7yjig8msvlbgftd5grevb'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

# database connection data
conf_name = 'settings.ini'
config = configparser.ConfigParser()
config.read(os.path.join(app.root_path, conf_name))
dbase = None

# login manager
login_manager = LoginManager(app)
login_manager.login_view = 'index'


@login_manager.user_loader
def load_user(user_id):
    return Userlogin().load_from_db(user_id, dbase)


# database connectors
def connect_db():
    global config
    params = dict(config['Database'])
    connect = psycopg2.connect(**params)
    return connect


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = BDatabaseTest(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


#   ------------------------
#   PAGES
#   ------------------------


@app.route('/')
def index():
    login_form = Loginform()
    reg_form = Registerform()

    return render_template('index.html', title='Вход и авторизация',
                           login_form=login_form, reg_form=reg_form)


@app.route('/login', methods=['POST'])
def login():
    login_form = Loginform()

    if login_form.validate_on_submit():
        email, psw = login_form.email_login.data, login_form.psw_login.data
        userdata = dbase.get_user_by_email(email)
        if userdata:
            user = userify(userdata)
        else:
            flash('Пользователь не найден', category='error')
            return redirect(url_for('index'))

        if check_password_hash(user['pass_hash'], psw):
            userlogin = Userlogin().create(user)
            rem = login_form.remember_login.data
            login_user(userlogin, remember=rem)
            # request.args.get('next') or url_for('profile')
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль', category='error')

    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    reg_form = Registerform()

    if reg_form.validate_on_submit():
        pswhash = generate_password_hash(reg_form.psw_reg.data)
        userinfo = {
            'email': reg_form.email_reg.data, 'pass_hash': pswhash,
            'lname': reg_form.lname_reg.data, 'fname': reg_form.fname_reg.data
        }
        res = dbase.add_user(**userinfo)

        if res:
            flash('Регистрация прошла успешно', category='success')
        else:
            flash('Пользователь с данной почтой уже зарегистрирован',
                  category='error')

    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из профиля', category='success')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль')


if __name__ == '__main__':
    app.run(debug=True)
