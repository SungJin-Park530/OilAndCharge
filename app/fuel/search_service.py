from .coordinate_service import CoordinateService
from .kakao_service import KakaoMobilityService
from .opinet_service import OpinetService
from .repository import StationRepository
from .services import StationCostService

from app.vehicle.services import VehicleService


class FuelSearchService:
    """
    주변 주유소 검색부터 실질 비용 계산까지의
    전체 비즈니스 흐름을 조합하는 서비스 클래스.

    각 세부 기능은 전용 서비스에 위임하고,
    이 클래스는 전체 처리 순서만 담당함.

    처리 흐름
    ----------
    1. 차량 정보 조회
    2. WGS84 → KATEC 좌표 변환
    3. OPINET 주변 주유소 조회
    4. 주유소/가격 정보 DB 저장
    5. Kakao Mobility 실제 도로거리 조회
    6. 주유소별 실질 비용 계산
    7. 실질 총비용 기준 정렬
    """

    def __init__(
        self,
        opinet_api_key,
        kakao_api_key
    ):
        """
        외부 API 사용에 필요한 인증키를 전달받아
        각 API 서비스 객체를 생성함.
        """

        self.opinet_service = OpinetService(
            opinet_api_key
        )

        self.kakao_service = KakaoMobilityService(
            kakao_api_key
        )

    def search(
        self,
        vehicle_id,
        fuel_amount,
        longitude,
        latitude,
        radius=3000
    ):
        """
        사용자 위치 주변의 주유소를 조회하고
        차량 연비와 주유량을 반영한 실질 비용을 계산함.

        Parameters
        ----------
        vehicle_id : int
            사용자가 선택한 차량 ID

        fuel_amount : float
            사용자가 주유할 양(L)

        longitude : float
            사용자 현재 위치 경도(WGS84)

        latitude : float
            사용자 현재 위치 위도(WGS84)

        radius : int
            OPINET 검색 반경(m)
            현재 MVP 기본값은 3000m

        Returns
        -------
        dict
            차량 정보, 주유량, 검색 위치,
            비용 계산이 완료된 주유소 목록
        """

        # 주유량은 반드시 0보다 커야 함.
        if fuel_amount <= 0:
            raise ValueError(
                "주유량은 0보다 커야 합니다."
            )

        # 현재 MVP에서 지원 가능한 차량인지 조회 및 검증
        vehicle = (
            VehicleService
            .get_vehicle_for_fuel_calculation(
                vehicle_id
            )
        )

        # OPINET 반경검색에서 사용할 수 있도록
        # 사용자 WGS84 좌표를 KATEC 좌표로 변환
        katec_x, katec_y = (
            CoordinateService.wgs84_to_katec(
                longitude,
                latitude
            )
        )

        # OPINET에서 주변 휘발유 주유소 검색
        stations = (
            self.opinet_service
            .get_nearby_stations(
                katec_x=katec_x,
                katec_y=katec_y,
                radius=radius,

                # 현재 기본 결과는 거리순으로 조회
                sort=2
            )
        )

        # 검색된 주유소가 없다면
        # 이후 카카오 API와 비용 계산을 수행하지 않음.
        if not stations:
            return {
                "vehicle": vehicle,
                "fuel_amount": fuel_amount,
                "location": {
                    "longitude": longitude,
                    "latitude": latitude
                },
                "stations": []
            }

        # OPINET에서 조회한 주유소 기본정보와 최신 가격을
        # Cloudtype MariaDB에 저장/갱신함.
        StationRepository.upsert_stations(
            stations
        )

        # 사용자 현재 위치에서 각 주유소까지의
        # 실제 자동차 도로거리와 예상시간을 조회함.
        stations_with_routes = (
            self.kakao_service
            .get_routes_to_stations(
                origin_longitude=longitude,
                origin_latitude=latitude,
                stations=stations
            )
        )

        # 차량 DB에 저장된 실제 연비와
        # 사용자가 입력한 주유량을 사용하여
        # 주유소별 이동비/주유비/총비용을 계산함.
        stations_with_costs = (
            StationCostService
            .calculate_station_costs(
                stations=stations_with_routes,
                fuel_efficiency=vehicle[
                    "fuel_efficiency"
                ],
                fuel_amount=fuel_amount
            )
        )

        # 실질 총비용이 낮은 주유소부터 반환함.
        sorted_stations = (
            StationCostService
            .sort_by_total_cost(
                stations_with_costs
            )
        )

        return {
            "vehicle": vehicle,
            "fuel_amount": fuel_amount,

            "location": {
                "longitude": longitude,
                "latitude": latitude
            },

            "stations": sorted_stations
        }