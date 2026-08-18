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
    
    @staticmethod
    def get_vehicles(owner=None):
        """
        현재 MVP에서 사용할 수 있는 휘발유 차량 목록을 조회함.

        owner가 전달되면 해당 소유주의 차량만 조회하고,
        전달되지 않으면 등록된 휘발유 차량 전체를 조회함.
        """

        if owner:
            return (
                VehicleRepository
                .get_gasoline_vehicles_by_owner(owner)
            )

        return (
            VehicleRepository
            .get_gasoline_vehicles()
        )


    @staticmethod
    def create_vehicle(
        owner,
        vehicle_name,
        fuel_efficiency,
        fuel_type
    ):
        """
        차량 등록 요청값을 검증한 뒤
        VehicleRepository를 통해 DB에 저장함.
        """

        # 앞뒤 공백 제거
        owner = owner.strip() if owner else ""
        vehicle_name = (
            vehicle_name.strip()
            if vehicle_name
            else ""
        )

        # 소유주 필수
        if not owner:
            raise ValueError(
                "소유주를 입력해주세요."
            )

        # 차량명 필수
        if not vehicle_name:
            raise ValueError(
                "차량명을 입력해주세요."
            )

        # DB 컬럼 길이에 맞춰 검증
        if len(owner) > 255:
            raise ValueError(
                "소유주 이름이 너무 깁니다."
            )

        if len(vehicle_name) > 255:
            raise ValueError(
                "차량명이 너무 깁니다."
            )

        # 연비 검증
        if fuel_efficiency is None:
            raise ValueError(
                "차량 연비를 입력해주세요."
            )

        if fuel_efficiency <= 0:
            raise ValueError(
                "차량 연비는 0보다 커야 합니다."
            )

        # -------------------------------------------------
        # 현재 MVP는 휘발유 차량만 지원함.
        #
        # DB에는 경유/LPG/전기 ENUM 값이 존재하지만
        # 현재 OPINET 검색과 비용 계산은 B027(휘발유)을
        # 기준으로 구현되어 있으므로 휘발유만 등록 허용.
        # -------------------------------------------------
        if fuel_type != "휘발유":
            raise ValueError(
                "현재는 휘발유 차량만 지원합니다."
            )

        return VehicleRepository.create_vehicle(
            owner=owner,
            vehicle_name=vehicle_name,
            fuel_efficiency=fuel_efficiency,
            fuel_type=fuel_type
        )