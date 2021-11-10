# system import
import os
import psycopg2
import configparser
from flask import Flask, g, render_template, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

# self import
from bamboo_forms import Loginform, Registerform
from bamboo_database_test import BDatabaseTest
from bamboo_userlogin import Userlogin

# config
DEBUG = True
SECRET_KEY = 'kmgdtjnosfepplrgb7yjig8msvlbgftd5grevb'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

# database data
conf_name = 'settings.ini'
config = configparser.ConfigParser()
config.read(os.path.join(app.root_path, conf_name))
dbase = None


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
    return render_template('index.html', title='Основная')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = Loginform()
    reg = Registerform()

    if login.validate_on_submit():
        print(login.email_input.data)
        print(login.psw_input.data)

    elif reg.validate_on_submit():
        print(reg.fname_reg.data)
        print(reg.lname_reg.data)
        print(reg.email_reg.data)
        print(reg.psw_reg.data)
        print(reg.psw2_reg.data)

    return render_template('register.html', title='Вход и регистрация',
                           login_form=login, reg_form=reg)


if __name__ == '__main__':
    app.run(debug=True)
