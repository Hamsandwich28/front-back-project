import os
import psycopg2
import configparser
from flask import Flask, render_template, redirect, url_for
from flask import request, g
from bamboo_database import BDatabase


app = Flask(__name__)
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
    dbase = BDatabase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


#   ------------------------
#   PAGES
#   ------------------------


@app.route('/')
def index():
    return render_template('index.html', title='Главная', nav=dbase.get_menu())


if __name__ == '__main__':
    app.run(debug=True)
