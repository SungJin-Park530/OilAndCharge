import pymysql

from flask import g, current_app


def get_db():
    """
    현재 요청(Request)에서 사용할 DB 연결 객체를 반환함.

    Flask의 g 객체를 사용하여 하나의 HTTP 요청 안에서는
    동일한 DB 연결을 재사용함.

    아직 DB 연결이 생성되지 않았다면 config.py에 설정된
    MariaDB 접속 정보를 이용하여 새 연결을 생성함.
    """

    # 현재 요청에서 아직 DB 연결을 생성하지 않은 경우
    # MariaDB에 새로 연결함.
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["DB_HOST"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
            port=current_app.config["DB_PORT"],

            # 한글 및 이모지 등을 정상적으로 저장하기 위해
            # utf8mb4 문자셋 사용
            charset="utf8mb4",

            # SELECT 결과를 튜플이 아닌
            # {"column": value} 형태의 딕셔너리로 반환하도록 설정
            cursorclass=pymysql.cursors.DictCursor
        )

    return g.db


def close_db(error=None):
    """
    HTTP 요청이 종료될 때 사용한 DB 연결을 닫음.

    Flask의 g 객체에 저장되어 있던 DB 연결을 제거한 뒤
    실제 MariaDB 연결도 종료함.
    """

    # g 객체에서 DB 연결을 제거함.
    # 연결이 존재하지 않는 경우 None을 반환함.
    db = g.pop("db", None)

    # 생성된 DB 연결이 존재하는 경우 연결 종료
    if db is not None:
        db.close()


def init_db(app):
    """
    Flask 애플리케이션에 DB 종료 함수를 등록함.

    각 HTTP 요청 처리가 끝날 때 close_db()가 자동으로 호출되어
    사용한 DB 연결이 정상적으로 반환되도록 함.
    """

    app.teardown_appcontext(close_db)