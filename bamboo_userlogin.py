from flask import url_for
from flask_login import UserMixin


def userify(userdata):
    if isinstance(userdata, tuple):
        id_user, email, pass_hash, lastname, firstname, avatar = userdata
    else:
        id_user, email, pass_hash, lastname, firstname, avatar = userdata.values()

    if isinstance(avatar, memoryview):
        avatar = avatar.tobytes()

    return {
        'id_user': id_user,
        'email': email,
        'pass_hash': pass_hash,
        'lastname': lastname,
        'firstname': firstname,
        'avatar': avatar
    }


class Userlogin(UserMixin):
    def create(self, user):
        self.__user = user
        return self

    def load_from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def get_id(self):
        self.__user = userify(self.__user)
        return str(self.__user['id_user'])

    def get_email(self):
        self.__user = userify(self.__user)
        return self.__user['email'] if self.__user else 'Nomail'

    def get_fname(self):
        self.__user = userify(self.__user)
        return self.__user['firstname'] if self.__user else 'Noname'

    def get_lname(self):
        self.__user = userify(self.__user)
        return self.__user['lastname'] if self.__user else 'Noname'

    def get_passhash(self):
        self.__user = userify(self.__user)
        return self.__user['pass_hash']

    def get_avatar(self, app):
        img = None
        self.__user = userify(self.__user)
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), 'rb') as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Standart file wasn't found. " + str(e))
        else:
            img = self.__user['avatar']

        return img

    def verify_ext(self, filename):
        ext = filename.split('.', 1)[1]
        if ext.lower() == 'png':
            return True

        return False
