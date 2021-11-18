from flask import url_for
from flask_login import UserMixin
from binascii import hexlify


def userify(userdata):
    id_user, email, pass_hash, lastname, firstname, avatar = userdata
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
