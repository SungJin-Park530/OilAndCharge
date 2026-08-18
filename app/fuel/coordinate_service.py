from pyproj import CRS, Transformer


class CoordinateService:
    """
    WGS84 좌표와 오피넷에서 사용하는 KATEC(TM128) 좌표 사이의
    변환을 담당하는 서비스 클래스.

    WGS84
    - 일반적인 GPS 및 카카오맵에서 사용하는 경도/위도 좌표계

    KATEC(TM128)
    - 오피넷 반경 내 주유소 API에서 사용하는 좌표계
    """

    # 일반 GPS 및 지도 서비스에서 사용하는 WGS84 좌표계
    WGS84_CRS = CRS.from_epsg(4326)

    # 오피넷 KATEC 좌표 변환에 사용할 TM128 정의.
    #
    # 오피넷 공식 문서에서는 KATEC 좌표 사용 여부만 명시하고
    # 정확한 좌표계 정의 문자열은 제공하지 않음.
    #
    # 따라서 프로젝트 SCOPE에서 참고한 기존 TM128 변환 정의를
    # 현재 MVP의 변환 기준으로 사용함.
    KATEC_CRS = CRS.from_proj4(
        "+proj=tmerc "
        "+lat_0=38 "
        "+lon_0=128 "
        "+k=0.9999 "
        "+x_0=400000 "
        "+y_0=600000 "
        "+ellps=bessel "
        "+towgs84=-146.43,507.89,681.46 "
        "+units=m "
        "+no_defs"
    )

    # WGS84 → KATEC 변환기
    #
    # Transformer를 매 호출마다 새로 만들지 않고
    # 클래스에서 한 번 생성하여 재사용함.
    #
    # always_xy=True를 사용하면 입력 순서를
    # (경도, 위도) 즉 (x, y) 형태로 고정할 수 있음.
    _to_katec = Transformer.from_crs(
        WGS84_CRS,
        KATEC_CRS,
        always_xy=True
    )

    # KATEC → WGS84 역변환기
    _to_wgs84 = Transformer.from_crs(
        KATEC_CRS,
        WGS84_CRS,
        always_xy=True
    )

    @classmethod
    def wgs84_to_katec(cls, longitude, latitude):
        """
        WGS84 경도/위도를 KATEC 좌표로 변환함.

        Parameters
        ----------
        longitude : float
            경도. 예: 서울 약 126.x

        latitude : float
            위도. 예: 서울 약 37.x

        Returns
        -------
        tuple
            (KATEC X좌표, KATEC Y좌표)
        """

        # 경도 범위 검증
        if not -180 <= longitude <= 180:
            raise ValueError("경도 값이 올바르지 않습니다.")

        # 위도 범위 검증
        if not -90 <= latitude <= 90:
            raise ValueError("위도 값이 올바르지 않습니다.")

        # pyproj를 이용하여 WGS84 → KATEC 변환
        x, y = cls._to_katec.transform(
            longitude,
            latitude
        )

        return x, y

    @classmethod
    def katec_to_wgs84(cls, x, y):
        """
        KATEC 좌표를 WGS84 경도/위도로 변환함.

        OPINET API에서 받은 GIS_X_COOR, GIS_Y_COOR 값을
        카카오맵이나 Kakao Mobility에서 사용할 수 있는
        WGS84 좌표로 변환할 때 사용함.

        Returns
        -------
        tuple
            (경도, 위도)
        """

        # pyproj를 이용하여 KATEC → WGS84 역변환
        longitude, latitude = cls._to_wgs84.transform(
            x,
            y
        )

        return longitude, latitude