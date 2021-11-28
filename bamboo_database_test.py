# system import
import psycopg2
from datetime import datetime, timedelta
from iteration_utilities import deepflatten


def conference_view(datalist):
    if type(datalist) is list:
        conf_data = [{
            'id_conf': row[0],
            'title': row[1],
            'description': row[2],
            'time_conf': row[3],
            'creator_lastname': row[4],
            'creator_firstname': row[5],
            'id_creator': row[6],
            'is_active': row[3] <= datetime.now() <= row[3] + timedelta(hours=1)
        } for row in datalist]

        return conf_data
    else:
        raise TypeError("Тип должен быть списком")


class BDatabaseTest:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def add_user(self, email, pass_hash, lname, fname):
        try:
            sql = f"SELECT COUNT(email) FROM users WHERE email = '{email}';"
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            res, *other = list(deepflatten(res))
            if res > 0:
                return False

            sql = '''
            INSERT INTO users (email, pass_hash, lastname, firstname) 
            VALUES(%s, %s, %s, %s);
            '''
            self.__cur.execute(sql, (email, pass_hash, lname, fname))
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка добавления пользователя -> ', e)

        return False

    def get_user(self, id_user):
        try:
            sql = f"SELECT * FROM users WHERE id_user = {id_user} LIMIT 1;"
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if not res:
                return False

            return res
        except psycopg2.Error as e:
            print('Ошибка получения пользователя -> ', e)

        return False

    def get_user_by_email(self, email):
        try:
            sql = f"SELECT * FROM users WHERE email = '{email}' LIMIT 1;"
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if not res:
                return False

            return res
        except psycopg2.Error as e:
            print('Ошибка получения пользователя -> ', e)

        return False

    def add_conference(self, title, description, time_conf, id_creator):
        try:
            sql = '''
            INSERT INTO conferences (title, description, time_conf, id_creator)
            VALUES(%s, %s, %s, %s) RETURNING id_conf;
            '''
            self.__cur.execute(sql, (title, description, time_conf, id_creator))
            res = list(self.__cur.fetchone())
            id_created = res.pop()

            sql = '''
            INSERT INTO user_conf (id_user, id_conf)
            VALUES(%s, %s);
            '''
            self.__cur.execute(sql, (id_creator, id_created))
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка добавления записи конференции -> ', e)

        return False

    def get_conference(self, id_conf):
        try:
            sql = f"""
            SELECT * FROM conferences
            WHERE id_conf = {id_conf}
            LIMIT 1;"""
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res:
                res = conference_view([res]).pop()
                return res
        except psycopg2.Error as e:
            print('Ошибка чтения записи конференции -> ', e)

        return False

    def is_conf_member(self, id_conf, id_user):
        try:
            sql = f"""
            SELECT * FROM user_conf
            WHERE id_user = {id_user}
            AND id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res:
                return True
        except psycopg2.Error as e:
            print('Ошибка чтения -> ', e)

        return False

    def get_conferences(self, id_user):
        try:
            sql = f"""
            SELECT conferences.id_conf, title, description, time_conf, lastname, firstname, id_creator
            FROM user_conf JOIN conferences ON user_conf.id_conf = conferences.id_conf
            JOIN users ON conferences.id_creator = users.id_user
            WHERE user_conf.id_user = {id_user};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            conf_data = conference_view(res)

            return conf_data
        except psycopg2.Error as e:
            print('Ошибка чтения записей конференций -> ', e)

        return False

    def check_member_conference(self, id_user, id_conf):
        try:
            sql = f"""
            SELECT COUNT(*) FROM user_conf
            WHERE id_user = {id_user}
            AND id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if int(*res) > 0:
                return True

        except psycopg2.Error as e:
            print('Ошибка чтения записей конференций -> ', e)

        return False

    def add_member_conference(self, id_user, id_conf):
        try:
            sql = """
            INSERT INTO user_conf
            VALUES(%s, %s);"""
            self.__cur.execute(sql, (id_user, id_conf))
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка добавления записей конференций -> ', e)

        return False

    def get_creator_id_conference(self, id_conf):
        try:
            sql = f"""
            SELECT users.id_user
            FROM users JOIN conferences ON users.id_user = conferences.id_creator
            WHERE conferences.id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = list(deepflatten(self.__cur.fetchall()))
            if res:
                return res.pop()
        except psycopg2.Error as e:
            print('Ошибка добавления записей конференций -> ', e)

        return False

    def get_members_conference(self, id_conf):
        try:
            sql = f"""
            SELECT users.lastname, users.firstname, users.email
            FROM user_conf JOIN users ON user_conf.id_user = users.id_user
            WHERE id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()

            return res
        except psycopg2.Error as e:
            print('Ошибка добавления записей конференций -> ', e)

        return False

    def remove_member_conference(self, id_user, id_conf):
        try:
            if id_user == self.get_creator_id_conference(id_conf):
                return False
            sql = f"""
            DELETE FROM user_conf
            WHERE id_user = {id_user}
            AND id_conf = {id_conf};"""
            self.__cur.execute(sql)
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка добавления записей конференций -> ', e)

        return False
