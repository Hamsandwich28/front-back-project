# system import
import psycopg2
import time
from datetime import datetime, timedelta
from iteration_utilities import deepflatten
from math import floor


def conference_view(datalist, conferences_filter):
    if type(datalist) is list:
        conf_data = [{
            'id_conf': row[0],
            'title': row[1],
            'description': row[2],
            'time_conf': row[3],
            'creator_lastname': row[4],
            'creator_firstname': row[5],
            'id_creator': row[6],
            'is_active': conferences_filter(row[0])
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

    def update_user_avatar(self, id_user, avatar):
        if not avatar:
            return False

        try:
            binary = psycopg2.Binary(avatar)
            sql = """
            UPDATE users
            SET avatar = %s
            WHERE id_user = %s;"""
            self.__cur.execute(sql, (binary, id_user))
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка обновления аватара', e)

        return False

    def update_password(self, id_user, pass_hash):
        try:
            sql = """
            UPDATE users
            SET pass_hash = %s
            WHERE id_user = %s;"""
            self.__cur.execute(sql, (pass_hash, id_user))
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка обновления пароля', e)

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
            WHERE user_conf.id_user = {id_user}
            ORDER BY time_conf;"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            conf_data = conference_view(res, self.active_conference_filter)

            return conf_data
        except psycopg2.Error as e:
            print('Ошибка чтения записей конференций -> ', e)

        return False

    def delete_conference(self, id_conf):
        try:
            sql = f"""
            DELETE FROM conferences
            WHERE id_conf = {id_conf};"""
            self.__cur.execute(sql)
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print("Ошибка удаления конференции -> ", e)

        return False

    def check_member_conference(self, id_user, id_conf):
        try:
            sql1 = f"""
            SELECT COUNT(*) FROM user_conf
            WHERE id_user = {id_user}
            AND id_conf = {id_conf};"""
            self.__cur.execute(sql1)
            res1 = self.__cur.fetchone()

            sql2 = f"""
            SELECT COUNT(*) FROM user_invite
            WHERE id_user = {id_user}
            AND id_conf = {id_conf};"""
            self.__cur.execute(sql2)
            res2 = self.__cur.fetchone()

            if int(*res1) > 0 or int(*res2) > 0:
                return True

        except psycopg2.Error as e:
            print('Ошибка чтения записей конференций -> ', e)

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

    def remove_invited_member(self, id_user, id_conf):
        try:
            sql = f"""
            DELETE FROM user_invite
            WHERE id_user = {id_user}
            AND id_conf = {id_conf}"""
            self.__cur.execute(sql)
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка удаления записи приглашений -> ', e)

        return False

    def remove_accepted_member(self, id_user, id_conf):
        try:
            sql = f"""
            DELETE FROM user_conf
            WHERE id_user = {id_user}
            AND id_conf = {id_conf}"""
            self.__cur.execute(sql)
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка удаления записи конференции -> ', e)

        return False

    def remove_member_conference(self, id_user, id_conf):
        if id_user == self.get_creator_id_conference(id_conf):
            return False

        invited = self.remove_invited_member(id_user, id_conf)
        accepted = self.remove_accepted_member(id_user, id_conf)
        return invited or accepted

    def get_invited_users(self, id_conf):
        try:
            sql = f"""
            SELECT id_user FROM user_invite
            WHERE user_invite.id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            res = list(deepflatten(res))

            return res
        except psycopg2.Error as e:
            print('Ошибка чтения записей приглашения -> ', e)

        return False

    def get_accepted_users(self, id_conf):
        try:
            sql = f"""
            SELECT id_user FROM user_conf
            WHERE user_conf.id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            res = list(deepflatten(res))

            return res
        except psycopg2.Error as e:
            print('Ошибка чтения записей приглашения -> ', e)

        return False

    def send_invitation(self, id_user, id_conf):
        try:
            if (
                id_user == self.get_creator_id_conference(id_conf) or
                id_user in self.get_accepted_users(id_conf)
            ):
                return False

            sql = """
            INSERT INTO user_invite
            VALUES (%s, %s, %s);"""
            self.__cur.execute(sql, (id_user, id_conf, int(time.time())))
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка добавления записей приглашения -> ', e)

        return False

    def get_invitations(self, id_user):
        try:
            sql = f"""
            SELECT conferences.id_conf, conferences.title, conferences.time_conf, lastname, firstname
            FROM user_invite JOIN conferences ON user_invite.id_conf = conferences.id_conf JOIN users
            ON conferences.id_creator = users.id_user
            WHERE user_invite.id_user = {id_user};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()

            return res
        except psycopg2.Error as e:
            print('Ошибка чтения записей приглашений -> ', e)

        return False

    def accept_invitation(self, id_user, id_conf):
        try:
            if (
                id_user not in self.get_invited_users(id_conf) or
                id_user in self.get_accepted_users(id_conf)
            ):
                return False

            sql = f"""
            INSERT INTO user_conf
            VALUES (%s, %s);"""
            self.__cur.execute(sql, (id_user, id_conf))

            sql = f"""
            DELETE FROM user_invite
            WHERE id_user = {id_user} AND id_conf = {id_conf}"""
            self.__cur.execute(sql)
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print('Ошибка записи приглашений -> ', e)

        return False

    def get_visited_users(self, id_conf):
        try:
            sql = f"""
            SELECT id_user, users.lastname, users.firstname, users.email
            FROM user_conf JOIN users ON user_conf.id_user = users.id_user
            WHERE last_visited = true AND id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchall()

            sql = f"""
            UPDATE user_conf SET last_visited = false
            WHERE id_conf = {id_conf};"""
            self.__cur.execute(sql)
            self.__db.commit()

            return res
        except psycopg2.Error as e:
            self.__db.rollback()
            print("Ошибка изменения данных времени конференции -> ", e)

        return False

    def update_time_conference(self, id_conf, start, period):
        try:
            sql = f"""
            UPDATE conferences
            SET time_conf = '{start + period}'
            WHERE id_conf = {id_conf};"""
            self.__cur.execute(sql)
            self.__db.commit()

            return True
        except psycopg2.Error as e:
            self.__db.rollback()
            print("Ошибка изменения данных времени конференции -> ", e)

        return False

    def active_conference_filter(self, id_conf):
        durable = 2  # два часа
        try:
            sql = f"""
            SELECT time_conf, period_conf FROM conferences
            WHERE id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if not res:
                return False

            start, period = res
            if start <= datetime.now() <= start + timedelta(hours=durable):
                return True
            elif datetime.now() < start:
                return False
            elif period:
                if self.update_time_conference(id_conf, start, period):
                    return self.active_conference_filter(id_conf)
                else:
                    raise psycopg2.Error("Ошибка изменения данных времени.")
            else:
                self.delete_conference(id_conf)

        except psycopg2.Error as e:
            print("Ошибка анализа данных конференции -> ", e)

        return False

    def skip_period(self, id_conf):
        # ДЛЯ ПРОПУСКА ДАЖЕ ИДУЩЕЙ КОНФЕРЕНЦИИ
        try:
            sql = f"""
            SELECT time_conf, period_conf FROM conferences
            WHERE id_conf = {id_conf};"""
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if not res:
                return False

            start, period = res
            if not period:
                self.delete_conference(id_conf)
            else:
                return self.update_time_conference(id_conf, start, period)

            return True
        except psycopg2.Error as e:
            print("Ошибка выполнения команды -> ", e)

        return False
