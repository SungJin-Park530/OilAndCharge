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

        Raises
        ------
        ValueError
            계산에 사용할 값이 유효하지 않은 경우 발생함.
        """

        # 연비는 이동에 필요한 연료량 계산의 나눗셈에 사용되므로
        # 반드시 0보다 큰 값이어야 함.
        if fuel_efficiency <= 0:
            raise ValueError("차량 연비는 0보다 커야 합니다.")

        # 주유량은 실제 주유할 양이므로
        # 0보다 큰 값만 허용함.
        if fuel_amount <= 0:
            raise ValueError("주유량은 0보다 커야 합니다.")

        # 이동거리는 음수가 될 수 없음.
        if round_trip_distance < 0:
            raise ValueError("이동 거리는 0 이상이어야 합니다.")

        # 리터당 유가는 비용 계산에 사용되므로
        # 0보다 큰 값만 허용함.
        if fuel_price <= 0:
            raise ValueError("주유 가격은 0보다 커야 합니다.")

        # 왕복 이동에 소비되는 연료 비용 계산
        #
        # 왕복 거리(km) ÷ 연비(km/L)
        # → 이동에 필요한 연료량(L)
        travel_cost = (
            round_trip_distance / fuel_efficiency
        ) * fuel_price

        # 주유 비용과 이동 비용을 합산하여
        # 실제로 소요되는 전체 비용을 계산함.
        total_cost = travel_cost + (
            fuel_price * fuel_amount
        )

        # 화면에서 원 단위 정수로 표시할 수 있도록 반올림함.
        return round(travel_cost), round(total_cost)
    
class StationCostService:
    """
    여러 주유소의 실제 도로거리와 유가를 이용하여
    주유소별 실제 소요 비용을 계산하는 서비스 클래스.

    Kakao Mobility와 OPINET에서 받은 데이터를
    FuelCalculator에 연결하는 역할을 담당함.

    이 클래스에서는 카드 할인 계산을 수행하지 않음.
    카드 할인 기능은 추후 별도의 카드 서비스와 연동함.
    """

    @staticmethod
    def calculate_station_costs(
        stations,
        fuel_efficiency,
        fuel_amount
    ):
        """
        여러 주유소의 비용을 한 번에 계산함.

        Parameters
        ----------
        stations : list
            KakaoMobilityService의 길찾기 결과가 포함된
            주유소 목록

        fuel_efficiency : float
            선택한 차량의 연비(km/L)

        fuel_amount : float
            사용자가 주유할 양(L)

        Returns
        -------
        list
            각 주유소에 비용 계산 결과가 추가된 목록
        """

        # 계산할 주유소가 없으면 빈 목록 반환
        if not stations:
            return []

        result_stations = []

        for station in stations:

            # 원본 데이터를 직접 변경하지 않기 위해
            # 새로운 딕셔너리로 복사해서 사용함.
            result = station.copy()

            # Kakao Mobility 길찾기에 실패한 주유소는
            # 정확한 이동비 계산이 불가능하므로
            # 비용값을 None으로 설정함.
            if (
                not station.get("route_available")
                or station.get("road_distance_m") is None
            ):
                result["one_way_distance_km"] = None
                result["round_trip_distance_km"] = None
                result["travel_cost"] = None
                result["fuel_cost"] = None
                result["total_cost"] = None
                result["cost_available"] = False

                result_stations.append(result)
                continue

            # Kakao Mobility의 distance는 미터(m) 단위이므로
            # 비용 계산에 사용할 km 단위로 변환함.
            one_way_distance_km = (
                station["road_distance_m"] / 1000
            )

            # 현재 MVP에서는 편도 실제 도로거리의 2배를
            # 왕복거리로 사용함.
            #
            # 추후 필요하다면
            # 주유소 → 사용자 복귀 경로를 별도로 계산하여
            # 더 정확한 왕복거리로 개선할 수 있음.
            round_trip_distance_km = (
                one_way_distance_km * 2
            )

            # OPINET에서 받은 해당 주유소의
            # 실제 리터당 판매 가격
            fuel_price = station["price"]

            # 기존 FuelCalculator를 사용하여
            # 왕복 이동비와 실질 총비용을 계산함.
            travel_cost, total_cost = (
                FuelCalculator.calculate_cost(
                    round_trip_distance=round_trip_distance_km,
                    fuel_efficiency=fuel_efficiency,
                    fuel_price=fuel_price,
                    fuel_amount=fuel_amount
                )
            )

            # 사용자가 실제로 주유하는 금액.
            #
            # 이동비를 제외한 순수 주유 비용을
            # 프론트에서도 별도로 표시할 수 있도록 계산함.
            fuel_cost = round(
                fuel_price * fuel_amount
            )

            # 프론트에서 사용하기 쉽도록
            # km 단위 거리와 비용 정보를 기존 주유소 데이터에 추가함.
            result["one_way_distance_km"] = round(
                one_way_distance_km,
                2
            )

            result["round_trip_distance_km"] = round(
                round_trip_distance_km,
                2
            )

            result["travel_cost"] = travel_cost
            result["fuel_cost"] = fuel_cost
            result["total_cost"] = total_cost

            # 정상적으로 비용 계산이 완료되었음을 표시함.
            result["cost_available"] = True

            result_stations.append(result)

        return result_stations
    
    @staticmethod
    def sort_by_total_cost(stations):
        """
        비용 계산이 완료된 주유소를
        실질 총비용(total_cost)이 낮은 순서로 정렬함.

        길찾기 또는 비용 계산에 실패한 주유소는
        정상 계산된 주유소 뒤에 배치함.
        """

        return sorted(
            stations,
            key=lambda station: (
                not station.get("cost_available", False),
                station.get("total_cost")
                if station.get("total_cost") is not None
                else float("inf")
            )
        )