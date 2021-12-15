# system import
import os
import ssl
import psycopg2
import configparser
from datetime import date
from time import localtime, strftime
from flask import Flask, g, render_template, url_for, request, \
    redirect, flash, make_response, jsonify
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# self import
from bamboo_forms import Loginform, Registerform, Createform, Addform, Removeform, Changepasswordform
from bamboo_database_test import BDatabaseTest
from bamboo_userlogin import Userlogin, userify

context = ssl.SSLContext()
context.load_cert_chain('cert.pem', 'key.pem')

# config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kmgdtjnosfepplrgb7yjig8msvlbgftd5grevb'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# database connection data
conf_name = 'settings.ini'
config = configparser.ConfigParser()
config.read(os.path.join(app.root_path, conf_name))
dbase = None

# login manager
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message = 'Пожалуйста, авторизуйтесь на сайте'
login_manager.login_message_category = 'success'


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
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

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
            return redirect(request.args.get('next') or url_for('profile'))
        else:
            flash('Неверный логин или пароль', category='error')
    else:
        flash('Неверный ввод полей', category='error')

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
            return redirect(url_for('index'))
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
    conferences = dbase.get_conferences(current_user.get_id())
    return render_template('profile.html', title='Профиль', conferences=conferences,
                           id_user=int(current_user.get_id()))


@app.route('/create_conference', methods=['GET', 'POST'])
@login_required
def create_conference():
    create_form = Createform()

    if create_form.validate_on_submit():
        if create_form.date_create.data < date.today():
            flash('Выберите будущий день', category='error')
            return redirect(url_for("create_conference"))

        activity_period = create_form.period_create.data
        conf_data = {
            'title': create_form.title_create.data,
            'description': create_form.description_create.data,
            'time_conf': f'{create_form.date_create.data} {create_form.time_create.data}',
            'period_conf':  activity_period if activity_period else None,
            'id_creator': current_user.get_id()
        }
        dbase.add_conference(**conf_data)
        flash('Конференция создана', category='success')
        return redirect(url_for("profile"))

    return render_template('create_conference.html',  title='Создание конференции',
                           create_form=create_form)


@app.route('/settings')
@login_required
def settings():
    changepassword = Changepasswordform()
    return render_template('settings.html', title="Настройка пользователя", change_password_form=changepassword)


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    changepassword = Changepasswordform()

    if changepassword.validate_on_submit():
        current_pass = changepassword.old_change.data
        new_pass = changepassword.psw_change.data
        if check_password_hash(current_user.get_passhash(), current_pass):
            dbase.update_password(int(current_user.get_id()), generate_password_hash(new_pass))
        else:
            flash("Текущий пароль неверный", category="error")
            return redirect(url_for('settings'))
    else:
        flash("Данные ввода некорректны", category="error")
        return redirect(url_for('settings'))

    flash("Пароль был обновлён", category="success")
    return redirect(url_for('profile'))


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file and current_user.verify_ext(filename=file.filename):
            try:
                img = file.read()
                res = dbase.update_user_avatar(current_user.get_id(), img)
                if not res:
                    flash('Аватар не был загружен', category='error')
                flash('Аватар обновлён', category='success')
            except FileNotFoundError:
                flash('Файл не найден', category='error')

    return redirect(url_for('profile'))


@app.route('/conference/<id_conf>')
@login_required
def chat_room(id_conf):
    conference = dbase.get_conference(id_conf)
    if conference and dbase.is_conf_member(id_conf, current_user.get_id()):
        if not dbase.is_conference_active(id_conf):
            flash("Конференция неактивна. ", category='error')
            return redirect(url_for('profile'))

        conference = {'id_conf': id_conf, 'title': conference[1]}
        fullname = f"{current_user.get_lname()} {current_user.get_fname()}"
        return render_template('chat_room.html', title=f"{conference['title']}",
                               userid=current_user.get_id(), username=fullname,
                               conference=conference)
    else:
        flash("Вы не являетесь членом этого чата.", category='error')
        return redirect(url_for('profile'))


@app.route('/getstory/<id_conf>', methods=['GET'])
@login_required
def get_chat_story(id_conf):
    rows = dbase.get_chat_story(id_conf)
    story_rows = [{
        "username": f"{row[0]} {row[1]}",
        "message": row[3]
    } for row in rows]
    return jsonify({"story": story_rows}), 200


@app.route('/conference/<id_conf>/edit', methods=['GET'])
@login_required
def chat_edit(id_conf):
    addform = Addform()
    removeform = Removeform()
    conference = dbase.get_conference(id_conf)
    if conference and dbase.is_conf_member(id_conf, current_user.get_id()):
        conference = {'id_conf': id_conf, 'title': conference[1],
                      'description': conference[2], 'time_conf': conference[3]}
        member_list = dbase.get_members_conference(id_conf)
        members = [{
            'lastname': row[0],
            'firstname': row[1],
            'email': row[2]
             } for row in member_list]
        return render_template('chat_edit.html', title=f"{conference['title']} EDIT",
                               conference=conference, members=members,
                               addmember_form=addform, removemember_form=removeform)

    return redirect(url_for('profile'))


@app.route('/conference/delete', methods=['DELETE'])
@login_required
def chat_delete():
    on_delete = int(request.json["on_delete"])
    if dbase.delete_conference(on_delete):
        flash("Конференция была удалена", category="success")
        return jsonify({"deleted": True}), 200
    else:
        return jsonify({"deleted": False}), 200


@app.route('/conference/<id_conf>/add', methods=['POST'])
@login_required
def chat_add_member(id_conf):
    addform = Addform()
    if addform.validate_on_submit():
        email = addform.email_add.data
        user_data = dbase.get_user_by_email(email)
        if user_data:
            id_user, *other = user_data
            if dbase.check_member_conference(id_user, id_conf):
                flash("Пользователь уже в конференции", category='success')
            else:
                dbase.send_invitation(id_user, id_conf)
                flash("Пользователю отослано приглашение", category='success')
                redirect(url_for('profile', id_conf=id_conf))
        else:
            flash("Пользователь не найден", category='error')

    return redirect(url_for('chat_edit', id_conf=id_conf))


@app.route('/conference/<id_conf>/remove', methods=['POST'])
@login_required
def chat_remove_member(id_conf):
    removeform = Removeform()
    if removeform.validate_on_submit():
        email = removeform.email_remove.data
        user_data = dbase.get_user_by_email(email)
        if user_data:
            id_user, *other = user_data
            if dbase.check_member_conference(id_user, id_conf):
                if dbase.remove_member_conference(id_user, id_conf):
                    flash("Пользователь удалён из конференции", category='success')
                else:
                    flash("Пользователь не мог быть удалён.", category='error')
            else:
                flash("Пользователя нет в конференции", category='error')
        else:
            flash("Пользователь не найден", category='error')

    return redirect(url_for('chat_edit', id_conf=id_conf))


@app.route('/invitations')
@login_required
def invitations():
    invitations_list = dbase.get_invitations(int(current_user.get_id()))
    invitation_rows = [{
        "id": row[0],
        "title": row[1],
        "time": row[2],
        "lastname": row[3],
        "firstname": row[4]
    } for row in invitations_list]
    return render_template('invitations.html', title='Приглашения', invitations=invitation_rows)


@app.route('/invitation_accept', methods=['POST'])
@login_required
def invitation_accept():
    try:
        str_id = str(request.json.get("accepted_id"))
        id_accepted = int(str_id.split("_")[1])
        if dbase.accept_invitation(int(current_user.get_id()), id_accepted):
            return jsonify({"accepted": True}), 200

        return jsonify({"accepted": False}), 200
    except... as e:
        print("Какая-то ошибка -> ", e)

    return "Mistaken", 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, ssl_context=context)
