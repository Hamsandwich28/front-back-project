# system import
import os
import psycopg2
import configparser
from time import localtime, strftime
from flask import Flask, g, render_template, url_for, request, redirect, flash, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash

# self import
from bamboo_forms import Loginform, Registerform, Createform
from bamboo_database_test import BDatabaseTest
from bamboo_userlogin import Userlogin, userify

# config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kmgdtjnosfepplrgb7yjig8msvlbgftd5grevb'
socketio = SocketIO(app)

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


@app.route('/userava')
@login_required
def userava():
    img = current_user.get_avatar(app)
    if not img:
        return ''

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/profile')
@login_required
def profile():
    dbase.get_conferences(current_user.get_id())
    return render_template('profile.html', title='Профиль')


@app.route('/create_conference', methods=['GET', 'POST'])
@login_required
def create_conference():
    create_form = Createform()

    if create_form.validate_on_submit():
        conf_data = {
            'title': create_form.title_create.data,
            'description': create_form.description_create.data,
            'time_conf': f'{create_form.date_create.data} {create_form.time_create.data}',
            'id_creator': current_user.get_id()
        }
        dbase.add_conference(**conf_data)

    return render_template('create_conference.html',  title='Создание конференции',
                           create_form=create_form)


@app.route('/conference')
@login_required
def conference():
    username = ' '.join([current_user.get_fname(), current_user.get_lname()])
    return render_template('conference.html', title='Конференция',
                           username=username)


@socketio.on('message')
def message(data):
    print(f'\n{data}\n')
    send({
        'msg': data['msg'],
        'username': data['username'],
        'time_spamp': strftime('%b-%d %I:%M%p', localtime())
    })


@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': f"{data['username']} присоединился к {data['room']}"}, room=data['room'])


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': f"{data['username']} вышел из {data['room']}"}, room=data['room'])


if __name__ == '__main__':
    socketio.run(app)
