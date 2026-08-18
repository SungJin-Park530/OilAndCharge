import requests


class KakaoMobilityService:
    """
    Kakao Mobility 길찾기 API를 이용하여
    사용자 위치에서 여러 주유소까지의 실제 자동차 이동거리와
    예상 소요시간을 조회하는 서비스 클래스.

    Kakao Maps JavaScript SDK의 지도 표시 기능과는 분리된 역할임.

    - JavaScript SDK
      → 프론트 지도/마커 표시

    - KakaoMobilityService
      → 백엔드 자동차 길찾기
    """

    # Kakao Mobility 일반 다중 목적지 길찾기 API
    BASE_URL = (
        "https://apis-navi.kakaomobility.com"
        "/v1/destinations/directions"
    )

    # 일반 다중 목적지 길찾기는
    # 한 요청당 최대 30개의 목적지를 지원함.
    MAX_DESTINATIONS = 30

    def __init__(self, api_key):
        """
        카카오디벨로퍼스에서 발급한 REST API 키를 전달받음.

        Client Secret이나 JavaScript 키가 아니라
        REST API 키 값을 사용해야 함.
        """

        if not api_key:
            raise ValueError(
                "Kakao REST API 키가 설정되어 있지 않습니다."
            )

        self.api_key = api_key

    def get_routes_to_stations(
        self,
        origin_longitude,
        origin_latitude,
        stations,
        priority="DISTANCE"
    ):
        """
        사용자 위치에서 여러 주유소까지의 실제 자동차 경로를 조회함.

        Parameters
        ----------
        origin_longitude : float
            사용자 위치 경도(WGS84)

        origin_latitude : float
            사용자 위치 위도(WGS84)

        stations : list
            OpinetService에서 반환된 주유소 목록

        priority : str
            경로 탐색 기준

            DISTANCE
                이동거리가 가장 짧은 경로

            TIME
                이동시간이 가장 짧은 경로

            현재 서비스는 이동거리를 기반으로 이동비용을
            계산하므로 DISTANCE를 기본값으로 사용함.

        Returns
        -------
        list
            기존 주유소 데이터에 아래 값이 추가된 목록

            road_distance_m
                실제 자동차 편도 이동거리(m)

            duration_sec
                예상 편도 이동시간(초)

            route_available
                길찾기 성공 여부
        """

        # 조회할 주유소가 없으면 외부 API를 호출하지 않음.
        if not stations:
            return []

        # 출발지 WGS84 경도 검증
        if not -180 <= origin_longitude <= 180:
            raise ValueError(
                "출발지 경도 값이 올바르지 않습니다."
            )

        # 출발지 WGS84 위도 검증
        if not -90 <= origin_latitude <= 90:
            raise ValueError(
                "출발지 위도 값이 올바르지 않습니다."
            )

        # Kakao Mobility에서 지원하는 우선순위 값 검증
        if priority not in ("DISTANCE", "TIME"):
            raise ValueError(
                "priority는 DISTANCE 또는 TIME이어야 합니다."
            )

        # 한 요청당 최대 30개이므로
        # 30개를 초과하는 경우 여러 요청으로 나누어 처리함.
        chunks = [
            stations[index:index + self.MAX_DESTINATIONS]
            for index in range(
                0,
                len(stations),
                self.MAX_DESTINATIONS
            )
        ]

        result_stations = []

        for station_chunk in chunks:

            # API 응답의 key를 사용하여 원래 OPINET 주유소와
            # 다시 연결하기 위한 임시 매핑 데이터
            station_map = {}

            destinations = []

            for station in station_chunk:

                # Kakao Mobility는 WGS84 경도/위도를 사용하므로
                # OpinetService에서 변환한 longitude/latitude가 필요함.
                longitude = station.get("longitude")
                latitude = station.get("latitude")

                # 좌표가 없는 주유소는 길찾기를 요청할 수 없으므로
                # 실패 상태로 바로 결과에 포함함.
                if longitude is None or latitude is None:
                    failed_station = station.copy()
                    failed_station["road_distance_m"] = None
                    failed_station["duration_sec"] = None
                    failed_station["route_available"] = False

                    result_stations.append(
                        failed_station
                    )

                    continue

                station_key = str(
                    station["uni_id"]
                )

                station_map[station_key] = station

                # 다중 목적지 API에 전달할 목적지 정보
                destinations.append({
                    "x": longitude,
                    "y": latitude,

                    # OPINET의 주유소 고유 ID를 key로 사용하여
                    # 응답 결과와 원본 주유소를 다시 연결함.
                    "key": station_key
                })

            # 유효한 목적지가 하나도 없는 경우
            # 카카오 API를 호출할 필요가 없음.
            if not destinations:
                continue

            # 다중 목적지 길찾기 요청 Body
            payload = {
                "origin": {
                    "x": origin_longitude,
                    "y": origin_latitude
                },

                "destinations": destinations,

                # 길찾기 탐색 반경.
                # Kakao Mobility 다중 목적지 API의 최대값은 10km.
                "radius": 10000,

                # 현재 서비스는 이동 연료비를 거리 기준으로
                # 계산하므로 최단 거리 경로를 사용함.
                "priority": priority
            }

            # Kakao Mobility 인증 방식
            #
            # REST API 키 앞에 "KakaoAK "를 붙여
            # Authorization 헤더로 전달함.
            #
            # Client Secret은 여기에서 사용하지 않음.
            headers = {
                "Authorization": (
                    f"KakaoAK {self.api_key}"
                ),
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                # 4xx 또는 5xx 응답을 예외로 처리함.
                response.raise_for_status()

                # JSON 응답을 Python 객체로 변환함.
                data = response.json()

            except requests.RequestException as error:
                raise RuntimeError(
                    "Kakao Mobility 길찾기 API 호출에 실패했습니다."
                ) from error

            except ValueError as error:
                raise RuntimeError(
                    "Kakao Mobility API 응답을 해석할 수 없습니다."
                ) from error

            # 요청한 목적지별 길찾기 결과를 처리함.
            for route in data.get("routes", []):

                station_key = str(
                    route.get("key")
                )

                # 요청하지 않은 key가 응답에 들어온 경우
                # 잘못된 데이터이므로 무시함.
                if station_key not in station_map:
                    continue

                station = station_map[
                    station_key
                ].copy()

                # Kakao Mobility의 result_code가 0이면
                # 정상적으로 길찾기에 성공한 결과임.
                if route.get("result_code") == 0:

                    summary = route.get(
                        "summary",
                        {}
                    )

                    # 사용자 → 주유소 실제 자동차 이동거리(m)
                    station["road_distance_m"] = (
                        summary.get("distance")
                    )

                    # 사용자 → 주유소 예상 이동시간(초)
                    station["duration_sec"] = (
                        summary.get("duration")
                    )

                    station["route_available"] = True

                else:
                    # 특정 주유소의 길찾기만 실패한 경우
                    # 전체 주유소 검색을 실패시키지 않음.
                    station["road_distance_m"] = None
                    station["duration_sec"] = None
                    station["route_available"] = False

                result_stations.append(
                    station
                )

        return result_stations