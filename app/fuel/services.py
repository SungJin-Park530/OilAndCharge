class FuelCalculator:
    @staticmethod
    def calculate_cost(round_trip_distance, fuel_efficiency, fuel_price, fuel_amount):
        """
        - round_trip_distance: 왕복 거리 (km)
        - fuel_efficiency: 연비 (km/L)
        - fuel_price: 리터당 기름값 (원)
        - fuel_amount: 주유량 (L)
        """
        if fuel_efficiency <= 0:
            return 0, 0
            
        # 왕복 이동비용 = (왕복거리 ÷ 연비) × 리터당가격
        travel_cost = (round_trip_distance / fuel_efficiency) * fuel_price
        
        # 실질 소요 비용 = 왕복 이동비용 + (리터당가격 × 주유량)
        total_cost = travel_cost + (fuel_price * fuel_amount)
        
        return round(travel_cost), round(total_cost)