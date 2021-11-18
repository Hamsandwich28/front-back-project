# system import
import psycopg2
from iteration_utilities import deepflatten


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
            VALUES(%s, %s, %s, %s)
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

