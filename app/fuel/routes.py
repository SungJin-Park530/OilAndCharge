from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request
)

from .search_service import FuelSearchService
from .services import FuelCalculator

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


@fuel_bp.route("/api/stations", methods=["GET"])
def stations():
    """
    사용자 위치 주변의 주유소를 검색하고
    차량 연비와 주유량을 반영한 실질 비용을 반환함.

    Query Parameters
    ----------------
    vehicle_id : int
        사용자가 선택한 차량 ID

    amount : float
        주유량(L)

    lat : float
        사용자 현재 위치 위도

    lon : float
        사용자 현재 위치 경도

    Example
    -------
    /api/stations
        ?vehicle_id=1
        &amount=30
        &lat=37.566826
        &lon=126.9786567
    """

    try:
        # -------------------------------------------------
        # 1. Query Parameter 읽기
        # -------------------------------------------------

        vehicle_id = request.args.get(
            "vehicle_id",
            type=int
        )

        fuel_amount = request.args.get(
            "amount",
            type=float
        )

        latitude = request.args.get(
            "lat",
            type=float
        )

        longitude = request.args.get(
            "lon",
            type=float
        )

        # -------------------------------------------------
        # 2. 필수 요청값 검증
        # -------------------------------------------------

        if vehicle_id is None:
            return jsonify({
                "error": "vehicle_id가 필요합니다."
            }), 400

        if fuel_amount is None:
            return jsonify({
                "error": "amount가 필요합니다."
            }), 400

        if latitude is None:
            return jsonify({
                "error": "lat 값이 필요합니다."
            }), 400

        if longitude is None:
            return jsonify({
                "error": "lon 값이 필요합니다."
            }), 400

        # -------------------------------------------------
        # 3. 전체 주유소 검색 서비스 생성
        # -------------------------------------------------

        search_service = FuelSearchService(
            opinet_api_key=current_app.config[
                "OPINET_API_KEY"
            ],
            kakao_api_key=current_app.config[
                "KAKAO_REST_API_KEY"
            ]
        )

        # -------------------------------------------------
        # 4. 주변 주유소 검색 + 비용 계산
        # -------------------------------------------------

        result = search_service.search(
            vehicle_id=vehicle_id,
            fuel_amount=fuel_amount,
            longitude=longitude,
            latitude=latitude
        )

        # -------------------------------------------------
        # 5. 정상 결과 JSON 반환
        # -------------------------------------------------

        return jsonify(result), 200

    except ValueError as error:
        # 잘못된 차량 ID, 주유량, 좌표 등
        # 사용자의 요청값 문제
        return jsonify({
            "error": str(error)
        }), 400

    except RuntimeError as error:
        # OPINET 또는 Kakao Mobility와 같은
        # 외부 API 호출 실패
        return jsonify({
            "error": str(error)
        }), 502

    except Exception:
        # 예상하지 못한 오류는 서버 로그에 상세 내용을 기록하고,
        # 사용자에게는 내부 구현 정보를 노출하지 않음.
        current_app.logger.exception(
            "주유소 검색 중 예상하지 못한 오류 발생"
        )

        return jsonify({
            "error": "주유소 검색 처리 중 오류가 발생했습니다."
        }), 500


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
    
@fuel_bp.route("/calculate", methods=["POST"])
def calculate():
    """
    계산 요청을 받아 FuelCalculator에 전달하고
    계산 결과를 화면에 반환함.
    """

    try:
        # HTML form에서 전달된 문자열 값을
        # 계산 가능한 숫자 자료형으로 변환함.
        fuel_efficiency = float(request.form.get("efficiency", 0))
        fuel_amount = float(request.form.get("amount", 0))
        one_way_distance = float(request.form.get("distance", 0))
        fuel_price = float(request.form.get("price", 0))

        # 현재는 편도거리의 2배를 왕복거리로 사용함.
        # 추후 Kakao Mobility에서 받은 실제 도로거리로 대체할 예정.
        round_trip_distance = one_way_distance * 2

        # 실제 계산 규칙과 입력값 검증은
        # FuelCalculator가 담당함.
        travel_cost, total_cost = FuelCalculator.calculate_cost(
            round_trip_distance=round_trip_distance,
            fuel_efficiency=fuel_efficiency,
            fuel_price=fuel_price,
            fuel_amount=fuel_amount
        )

        # 계산 결과를 결과 페이지에 전달함.
        return render_template(
            "result.html",
            travel_cost=travel_cost,
            total_cost=total_cost
        )

    except ValueError as error:
        # 숫자 변환 실패 또는 FuelCalculator에서
        # 유효하지 않은 입력값을 발견한 경우 400 응답 반환
        return str(error), 400