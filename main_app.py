import os

from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms import RegisterForm

# REQ DELETE
menu = [{'title': 'Main', 'url': '/'},
        {'title': 'ToUser', 'url': '/user'}]

# config
# DATABASE = '/tmp/base.db'
DEBUG = True
SECRET_KEY = 'ofebkpf39j94gol,nfi094osv'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
# app.config.update(dict(DATABASE=os.path.join(app.root_path, '')))

# dbase = None
# login_manager = LoginManager(app)


@app.route('/')
def index():
    return render_template('index.html', title='Abama', menu=menu)


@app.route('/user')
def user():
    return render_template('user.html', title='User', menu=menu, username='titi')


if __name__ == '__main__':
    app.run(debug=True)
