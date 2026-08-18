from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)

from .services import VehicleService


# 차량 관련 API Blueprint
vehicle_bp = Blueprint(
    "vehicle",
    __name__
)


@vehicle_bp.route(
    "/api/vehicles",
    methods=["GET"]
)
def get_vehicles():
    """
    등록된 차량 목록을 조회함.

    Query Parameters
    ----------------
    owner : str, optional
        특정 소유주의 차량만 조회하고 싶을 경우 사용함.

    Examples
    --------
    전체 차량 조회:
        GET /api/vehicles

    특정 소유주:
        GET /api/vehicles?owner=test_user
    """

    try:
        # owner는 선택값.
        owner = request.args.get("owner")

        vehicles = VehicleService.get_vehicles(
            owner=owner
        )

        return jsonify({
            "count": len(vehicles),
            "vehicles": vehicles
        }), 200

    except Exception:
        current_app.logger.exception(
            "차량 목록 조회 중 오류 발생"
        )

        return jsonify({
            "error": "차량 목록 조회 중 오류가 발생했습니다."
        }), 500


@vehicle_bp.route(
    "/api/vehicles",
    methods=["POST"]
)
def create_vehicle():
    """
    새로운 차량을 등록함.

    Request JSON
    ------------
    {
        "owner": "test_user",
        "vehicle_name": "아반떼",
        "fuel_efficiency": 12.5,
        "fuel_type": "휘발유"
    }
    """

    try:
        # JSON 요청 데이터 읽기
        data = request.get_json(
            silent=True
        )

        # JSON 자체가 없는 요청 처리
        if not data:
            return jsonify({
                "error": "차량 정보가 필요합니다."
            }), 400

        # 문자열 데이터
        owner = data.get("owner")
        vehicle_name = data.get(
            "vehicle_name"
        )
        fuel_type = data.get(
            "fuel_type"
        )

        # -------------------------------------------------
        # 연비는 JSON 숫자로 들어오는 것이 정상이나,
        # 문자열 형태로 전달될 가능성도 고려해 float 변환함.
        # -------------------------------------------------
        try:
            fuel_efficiency = float(
                data.get("fuel_efficiency")
            )

        except (TypeError, ValueError):
            return jsonify({
                "error": "차량 연비가 올바르지 않습니다."
            }), 400

        # Service에서 실제 비즈니스 검증 및 DB 등록
        vehicle = VehicleService.create_vehicle(
            owner=owner,
            vehicle_name=vehicle_name,
            fuel_efficiency=fuel_efficiency,
            fuel_type=fuel_type
        )

        return jsonify({
            "message": "차량이 등록되었습니다.",
            "vehicle": vehicle
        }), 201

    except ValueError as error:
        # 잘못된 사용자 입력
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "차량 등록 중 오류 발생"
        )

        return jsonify({
            "error": "차량 등록 중 오류가 발생했습니다."
        }), 500