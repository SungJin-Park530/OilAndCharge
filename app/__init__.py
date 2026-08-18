from flask import Flask

from app.config import Config
from app.fuel.routes import fuel_bp
from app.models.database import init_db
from app.vehicle.routes import vehicle_bp


def create_app() -> Flask:
    """
    Flask 애플리케이션을 생성하고 초기 설정을 적용하는
    앱 팩토리 함수.
    """

    # Flask 애플리케이션 생성
    app = Flask(__name__)

    # 환경 변수 및 애플리케이션 설정 적용
    app.config.from_object(Config)

    # JSON 응답에서 한글을 \uXXXX 형태로 변환하지 않고
    # UTF-8 한글 문자열 그대로 반환하도록 설정함.
    #
    # Flask 2.3 이후 JSON_AS_ASCII 설정은 제거되었으므로
    # app.json.ensure_ascii 속성을 사용해야 함.
    app.json.ensure_ascii = False

    # 주유소 관련 Blueprint 등록
    app.register_blueprint(fuel_bp)
    
    # 차량 등록/조회 API Blueprint 등록
    app.register_blueprint(vehicle_bp)

    # 요청 종료 시 DB 연결이 자동으로 닫히도록 설정
    init_db(app)

    return app