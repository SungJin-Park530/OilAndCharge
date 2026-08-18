from flask import Blueprint, jsonify, render_template


# 주유소 관련 기능을 하나의 Blueprint로 관리함.
# 현재 프로젝트 규모에서는 별도의 main Blueprint를 만들지 않고,
# 메인 화면과 주유소 관련 화면을 fuel Blueprint에서 함께 관리함.
fuel_bp = Blueprint("fuel", __name__)


@fuel_bp.route("/")
def index():
    """
    메인 페이지를 반환함.

    사용자가 웹사이트의 기본 주소("/")로 접속했을 때
    templates/index.html 파일을 화면에 렌더링함.
    """
    return render_template("index.html")


@fuel_bp.route("/history")
def history():
    """
    계산 이력 페이지를 반환함.

    아직 DB 조회 기능은 구현하지 않았으므로
    임시로 빈 리스트를 전달함.

    추후 DB 기능 구현 시 records에 실제 계산 이력을 조회해서 전달할 예정.
    """
    records = []

    return render_template(
        "history.html",
        records=records
    )


@fuel_bp.route("/api/stations")
def stations():
    """
    주변 주유소 조회 API의 임시 경로.

    추후 OPINET API 연동이 완료되면
    실제 주변 주유소 목록을 반환하도록 수정할 예정.
    """
    return jsonify({
        "message": "주유소 조회 API 준비 중",
        "stations": []
    })


@fuel_bp.route("/health")
def health_check():
    """
    Flask 서버가 정상적으로 실행되고 있는지 확인하기 위한 경로.

    Cloudtype 배포 후에도 서버 동작 여부를 간단하게 확인하는 데 사용할 수 있음.
    """
    return jsonify({
        "status": "ok",
        "message": "OilAndCharge server is running"
    })