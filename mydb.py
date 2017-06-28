#coding:utf-8
import sqlite3

class DB(object):
    def __init__(self, db_name):
        self.conn=None
        self.cursor=None
        self.db_name=db_name

    def open(self):
        if self.conn and self.cursor:
            return True
        try:
            self.conn=sqlite3.connect(self.db_name)
            self.cursor=self.conn.cursor()
            return True
        except:
            self.conn = None
            self.cursor = None
            return False

    def insert(self, sql):
        if not self.conn or not self.cursor:
            return False

        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def update(self, sql):
        if not self.conn or not self.cursor:
            return False

        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def select(self, sql):
        if not self.conn or not self.cursor:
            return False        

        self.cursor.execute(sql)
        return True

    def fetchone(self):
        if not self.conn or not self.cursor:
            return []
        
        data = self.cursor.fetchone()
        if not data:
            return ''
        return data[0]

    def fetchall(self):
        if not self.conn or not self.cursor:
            return []

        return self.cursor.fetchall()
     
    def close(self):
        if not self.conn or not self.cursor:
            return False
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
