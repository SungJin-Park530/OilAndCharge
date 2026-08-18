import pymysql
from flask import g, current_app

def get_db():
    """��û(Request) ������ DB Ŀ�ؼ��� �����ϰų� ����"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            port=current_app.config['DB_PORT'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    """HTTP ��û ���� �� Ŀ�ؼ� ��ȯ"""
    db = g.pop('db', None)
    if db is not None:
        db.close()