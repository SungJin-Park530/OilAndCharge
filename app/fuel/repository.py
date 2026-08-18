from app.models.database import get_db


class StationRepository:
    """
    주유소와 유가 데이터를 MariaDB에 저장하고 조회하는
    Repository 클래스.

    외부 API 통신은 담당하지 않고
    DB 읽기/쓰기 작업만 담당함.
    """

    @staticmethod
    def upsert_stations(stations):
        """
        OPINET에서 조회한 주유소 목록을 DB에 저장함.

        station_info
        ----------------
        주유소의 기본정보를 저장함.
        이미 존재하는 주유소라면 최신 정보로 갱신함.

        fuel_price_cache
        ----------------
        주유소 + 유종별 최신 가격 한 건만 유지함.
        이미 가격 정보가 존재하면 INSERT하지 않고 UPDATE함.

        Parameters
        ----------
        stations : list
            OpinetService에서 정규화한 주유소 목록

        Returns
        -------
        int
            처리한 주유소 개수
        """

        # 저장할 데이터가 없는 경우 DB 작업을 하지 않음.
        if not stations:
            return 0

        # 현재 Flask 요청/Application Context에서 사용할
        # MariaDB 연결 객체를 가져옴.
        db = get_db()

        try:
            with db.cursor() as cursor:

                for station in stations:

                    # =====================================================
                    # 1. 주유소 기본정보 저장/갱신
                    # =====================================================
                    #
                    # uni_id가 station_info의 PK이므로
                    # 처음 발견한 주유소는 INSERT,
                    # 이미 존재하는 주유소는 UPDATE함.
                    #
                    # 가격은 변동 데이터이므로 station_info에
                    # 저장하지 않고 fuel_price_cache에서 따로 관리함.
                    station_sql = """
                        INSERT INTO station_info (
                            uni_id,
                            os_nm,
                            brand_code,
                            gis_x_coor,
                            gis_y_coor,
                            longitude,
                            latitude
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        ON DUPLICATE KEY UPDATE
                            os_nm = VALUES(os_nm),
                            brand_code = VALUES(brand_code),
                            gis_x_coor = VALUES(gis_x_coor),
                            gis_y_coor = VALUES(gis_y_coor),
                            longitude = VALUES(longitude),
                            latitude = VALUES(latitude)
                    """

                    cursor.execute(
                        station_sql,
                        (
                            station["uni_id"],
                            station["os_nm"],
                            station["brand_code"],
                            station["gis_x_coor"],
                            station["gis_y_coor"],
                            station["longitude"],
                            station["latitude"]
                        )
                    )

                    # =====================================================
                    # 2. 최신 유가 저장/갱신
                    # =====================================================
                    #
                    # fuel_price_cache에는
                    # UNIQUE(uni_id, product_code)가 설정되어 있으므로
                    # 같은 주유소 + 같은 유종 데이터가 이미 존재하면
                    # 새로운 행을 생성하지 않고 가격과 조회시간을 갱신함.
                    price_sql = """
                        INSERT INTO fuel_price_cache (
                            uni_id,
                            product_code,
                            price,
                            fetched_at
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            CURRENT_TIMESTAMP
                        )
                        ON DUPLICATE KEY UPDATE
                            price = VALUES(price),
                            fetched_at = CURRENT_TIMESTAMP
                    """

                    cursor.execute(
                        price_sql,
                        (
                            station["uni_id"],
                            station["product_code"],
                            station["price"]
                        )
                    )

            # 모든 주유소 저장이 성공한 경우에만
            # 트랜잭션을 실제 DB에 반영함.
            db.commit()

        except Exception:
            # 중간에 하나라도 저장 실패가 발생하면
            # 이번 작업에서 수행한 변경사항을 모두 취소함.
            db.rollback()

            # 호출한 쪽에서 오류를 확인할 수 있도록
            # 기존 예외를 다시 전달함.
            raise

        return len(stations)