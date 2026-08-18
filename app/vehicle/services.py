from .repository import VehicleRepository


class VehicleService:
    """
    차량 데이터를 비용 계산에서 사용할 수 있도록
    조회하고 검증하는 서비스 클래스.
    """

    @staticmethod
    def get_vehicle_for_fuel_calculation(vehicle_id):
        """
        비용 계산에 사용할 차량 정보를 반환함.

        현재 MVP에서는 휘발유 차량만 지원하므로
        다른 유종 차량을 선택하면 오류를 발생시킴.
        """

        # DB에서 차량 정보 조회
        vehicle = VehicleRepository.get_by_id(
            vehicle_id
        )

        # 존재하지 않는 차량 ID 처리
        if vehicle is None:
            raise ValueError(
                "존재하지 않는 차량입니다."
            )

        # 현재 MVP에서는 휘발유 차량만 지원
        if vehicle["fuel_type"] != "휘발유":
            raise ValueError(
                "현재는 휘발유 차량만 지원합니다."
            )

        # 연비가 잘못 저장된 차량은 계산에 사용할 수 없음
        if vehicle["fuel_efficiency"] <= 0:
            raise ValueError(
                "차량 연비 정보가 올바르지 않습니다."
            )

        return vehicle