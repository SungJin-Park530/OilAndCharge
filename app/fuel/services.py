class FuelCalculator:

    @staticmethod
    def calculate_cost(
        round_trip_distance,
        fuel_efficiency,
        fuel_price,
        fuel_amount
    ):
        """
        주유소까지 이동하는 비용과 실제 총 소요 비용을 계산함.

        Parameters
        ----------
        round_trip_distance : float
            주유소까지의 왕복 이동 거리(km)

        fuel_efficiency : float
            차량 연비(km/L)

        fuel_price : float
            주유소의 리터당 휘발유 가격(원/L)

        fuel_amount : float
            사용자가 주유할 양(L)

        Returns
        -------
        tuple
            (왕복 이동 비용, 실제 총 소요 비용)
        """

        # 연비가 0 이하이면 정상적인 연료 소비량 계산이 불가능함.
        if fuel_efficiency <= 0:
            return 0, 0

        # 왕복 이동에 소비되는 연료 비용 계산
        #
        # 왕복 거리(km) ÷ 연비(km/L)
        # → 이동에 필요한 연료량(L)
        #
        # 필요한 연료량 × 리터당 가격
        # → 왕복 이동 비용
        travel_cost = (
            round_trip_distance / fuel_efficiency
        ) * fuel_price

        # 실제 소요 비용 계산
        #
        # 왕복 이동 비용
        # +
        # 실제 주유 비용(리터당 가격 × 주유량)
        total_cost = travel_cost + (
            fuel_price * fuel_amount
        )

        # 화면에는 원 단위 정수로 표시하기 위해 반올림
        return round(travel_cost), round(total_cost)