from app.models.database import get_db


class VehicleRepository:
    """
    차량 정보에 대한 DB 조회를 담당하는 Repository 클래스.

    차량의 연비나 유종과 같은 데이터는 비용 계산에서 사용되지만,
    실제 DB 조회 책임은 FuelCalculator나 Fuel 관련 서비스가 아닌
    VehicleRepository에서 담당함.
    """

    @staticmethod
    def get_by_id(vehicle_id):
        """
        차량 ID를 이용하여 차량 한 대의 정보를 조회함.

        Parameters
        ----------
        vehicle_id : int
            vehicle 테이블의 PK

        Returns
        -------
        dict | None
            차량이 존재하면 차량 정보 딕셔너리를 반환하고,
            존재하지 않으면 None을 반환함.
        """

        db = get_db()

        sql = """
            SELECT
                vehicle_id,
                owner,
                vehicle_name,
                fuel_efficiency,
                fuel_type,
                card
            FROM vehicle
            WHERE vehicle_id = %s
        """

        with db.cursor() as cursor:
            cursor.execute(
                sql,
                (vehicle_id,)
            )

            return cursor.fetchone()

    @staticmethod
    def get_gasoline_vehicles():
        """
        현재 MVP에서 지원하는 휘발유 차량 목록을 조회함.

        전기차, 경유, LPG 차량은 DB에 존재하더라도
        현재 MVP 계산 대상에서는 제외함.

        Returns
        -------
        list
            휘발유 차량 목록
        """

        db = get_db()

        sql = """
            SELECT
                vehicle_id,
                owner,
                vehicle_name,
                fuel_efficiency,
                fuel_type,
                card
            FROM vehicle
            WHERE fuel_type = '휘발유'
            ORDER BY vehicle_id
        """

        with db.cursor() as cursor:
            cursor.execute(sql)

            return cursor.fetchall()

    @staticmethod
    def get_gasoline_vehicles_by_owner(owner):
        """
        특정 사용자가 등록한 휘발유 차량만 조회함.

        현재 사용자 인증 기능이 확정되지 않았으므로
        바로 메인 화면에서 사용하지는 않지만,
        추후 사용자별 차량 목록을 제공할 수 있도록 준비함.
        """

        db = get_db()

        sql = """
            SELECT
                vehicle_id,
                owner,
                vehicle_name,
                fuel_efficiency,
                fuel_type,
                card
            FROM vehicle
            WHERE owner = %s
              AND fuel_type = '휘발유'
            ORDER BY vehicle_id
        """

        with db.cursor() as cursor:
            cursor.execute(
                sql,
                (owner,)
            )

            return cursor.fetchall()