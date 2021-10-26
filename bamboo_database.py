import time
import math
import psycopg2
from flask import url_for


class BDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = 'SELECT title, url FROM navigation LIMIT 2;'
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return [{'title': tl, 'url': url} for tl, url in res]
        except psycopg2.Error as e:
            print(f'Ошибка чтения из базы данных -> {e}')

        return []
