from flask import Flask

from app.config import Config
from app.fuel.routes import fuel_bp
from app.models.database import init_db


def create_app() -> Flask:
    """
    Flask 애플리케이션을 생성하고 초기 설정을 적용하는
    앱 팩토리 함수.
    """

    # Flask 애플리케이션 생성
    app = Flask(__name__)

    # 환경 변수 및 애플리케이션 설정 적용
    app.config.from_object(Config)

    # 주유소 관련 Blueprint 등록
    app.register_blueprint(fuel_bp)

    # 요청 종료 시 DB 연결이 자동으로 닫히도록 설정
    init_db(app)

    return app