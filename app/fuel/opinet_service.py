import requests

from .coordinate_service import CoordinateService


class OpinetService:
    """
    OPINET API와의 통신을 담당하는 서비스 클래스.

    주요 역할
    ----------
    1. KATEC 좌표를 기준으로 주변 주유소 조회
    2. OPINET 응답 데이터 파싱
    3. 주유소의 KATEC 좌표를 WGS84 좌표로 변환
    4. 애플리케이션에서 사용하기 쉬운 형태로 데이터 정규화

    DB 저장은 이 클래스에서 담당하지 않음.
    DB 관련 작업은 추후 Repository 계층으로 분리함.
    """

    # OPINET 반경 내 주유소 검색 API
    BASE_URL = "https://www.opinet.co.kr/api/aroundAll.do"

    # 현재 MVP에서는 휘발유 차량만 지원하므로
    # 보통휘발유 제품 코드(B027)를 기본값으로 사용함.
    GASOLINE_PRODUCT_CODE = "B027"

    def __init__(self, api_key):
        """
        OPINET API 인증키를 전달받아 서비스 객체를 생성함.

        Config 또는 Flask에 직접 의존하지 않고 API 키를 외부에서
        전달받도록 하여 서비스 계층의 의존성을 줄임.
        """

        if not api_key:
            raise ValueError("OPINET API 키가 설정되어 있지 않습니다.")

        self.api_key = api_key

    def get_nearby_stations(
        self,
        katec_x,
        katec_y,
        radius=5000,
        sort=2,
        product_code=GASOLINE_PRODUCT_CODE
    ):
        """
        특정 KATEC 좌표를 기준으로 주변 주유소를 조회함.

        Parameters
        ----------
        katec_x : float
            검색 기준 위치의 KATEC X 좌표

        katec_y : float
            검색 기준 위치의 KATEC Y 좌표

        radius : int
            검색 반경(m)
            OPINET API 기준 최대 5000m

        sort : int
            정렬 기준
            1 = 가격순
            2 = 거리순

        product_code : str
            조회할 유종 코드
            현재 MVP에서는 B027(휘발유)을 사용함.

        Returns
        -------
        list
            정규화된 주유소 정보 목록
        """

        # OPINET에서 허용하는 최대 검색 반경을 벗어나는 값 방지
        if radius <= 0 or radius > 5000:
            raise ValueError(
                "검색 반경은 1m 이상 5000m 이하이어야 합니다."
            )

        # OPINET에서 지원하지 않는 정렬값 방지
        if sort not in (1, 2):
            raise ValueError(
                "정렬 기준은 1(가격순) 또는 2(거리순)만 가능합니다."
            )

        # OPINET API에 전달할 요청 파라미터 구성
        params = {
            "code": self.api_key,
            "out": "json",
            "x": katec_x,
            "y": katec_y,
            "radius": radius,
            "prodcd": product_code,
            "sort": sort
        }

        try:
            # 외부 API가 응답하지 않을 경우 무한 대기를 방지하기 위해
            # timeout을 설정함.
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=5
            )

            # 4xx / 5xx 응답일 경우 예외 발생
            response.raise_for_status()

            # OPINET JSON 응답을 Python 객체로 변환
            data = response.json()

        except requests.RequestException as error:
            # 네트워크 오류, timeout, HTTP 오류 등을
            # 서비스 계층의 오류로 변환함.
            raise RuntimeError(
                "OPINET API 호출에 실패했습니다."
            ) from error

        # OPINET 응답에서 실제 주유소 목록을 가져옴.
        #
        # 정상적인 응답 구조:
        #
        # {
        #     "RESULT": {
        #         "OIL": [...]
        #     }
        # }
        oils = data.get("RESULT", {}).get("OIL", [])

        # 검색 결과가 없을 경우 빈 리스트 반환
        if not oils:
            return []

        # 응답이 한 건일 경우 딕셔너리 형태로 올 가능성까지 고려하여
        # 이후 로직에서는 항상 리스트 형태로 처리함.
        if isinstance(oils, dict):
            oils = [oils]

        stations = []

        for oil in oils:

            # OPINET에서 받은 주유소의 KATEC 좌표
            station_x = float(oil.get("GIS_X_COOR", 0))
            station_y = float(oil.get("GIS_Y_COOR", 0))

            # 카카오맵과 Kakao Mobility API에서는 WGS84 좌표를
            # 사용해야 하므로 KATEC → WGS84 변환 수행
            longitude, latitude = (
                CoordinateService.katec_to_wgs84(
                    station_x,
                    station_y
                )
            )

            # OPINET 원본 필드명을 그대로 사용하지 않고
            # 이후 서비스/DB/프론트에서 사용하기 쉬운 이름으로 정규화함.
            station = {
                # OPINET에서 사용하는 주유소 고유 식별자
                "uni_id": oil.get("UNI_ID"),

                # 주유소 상호
                "os_nm": oil.get("OS_NM"),

                # 주유 브랜드 코드
                #
                # 공식 반환값 표에는 POLL_DIV_CD라고 되어 있지만,
                # 공식 응답 예시에서는 POLL_DIV_CO도 사용되고 있으므로
                # 두 필드를 모두 처리함.
                "brand_code": (
                    oil.get("POLL_DIV_CD")
                    or oil.get("POLL_DIV_CO")
                ),

                # 조회한 유종 코드
                "product_code": product_code,

                # 리터당 판매 가격
                "price": int(
                    float(oil.get("PRICE", 0))
                ),

                # OPINET이 계산하여 반환한 기준 위치와의 거리(m)
                #
                # 최종 비용 계산에는 이 값을 사용하지 않고,
                # 추후 Kakao Mobility에서 계산한 실제 도로거리를 사용함.
                "opinet_distance_m": float(
                    oil.get("DISTANCE", 0)
                ),

                # OPINET 원본 KATEC 좌표
                "gis_x_coor": station_x,
                "gis_y_coor": station_y,

                # CoordinateService를 통해 변환한 WGS84 좌표
                "longitude": longitude,
                "latitude": latitude
            }

            stations.append(station)

        return stations