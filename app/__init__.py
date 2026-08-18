from flask import Flask

from app.config import Config
from app.fuel.routes import fuel_bp


def create_app() -> Flask:
    """
    Flask 애플리케이션을 생성하고 설정하는 앱 팩토리 함수.

    앱 생성, 환경설정 적용, Blueprint 등록 등의 초기화 작업을
    한 곳에서 관리하기 위해 앱 팩토리 패턴을 사용함.
    """

    # Flask 애플리케이션 객체 생성
    app = Flask(__name__)

    # config.py에 정의된 환경설정 적용
    app.config.from_object(Config)

    # 주유소 관련 Blueprint 등록
    app.register_blueprint(fuel_bp)

    return app