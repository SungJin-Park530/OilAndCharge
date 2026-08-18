from flask import Blueprint, jsonify, render_template


fuel_bp = Blueprint("fuel - routes.py:4", __name__, url_prefix="/fuel")


@fuel_bp.route("/")
def index():
    return jsonify({
        "message": "Fuel API is running",
        "routes": [
            "/fuel",
            "/fuel/stations",
        ],
    })

@main_bp.route('/history') # type: ignore
def history():
    # DB에서 이력 데이터를 가져오는 로직 (예시)
    # records = db.get_fuel_records(10) 
    records = [] # 데이터가 없을 경우 빈 리스트 전달
    return render_template('history.html', records=records)

@fuel_bp.route("/stations")
def stations():
    return jsonify({
        "message": "Station list placeholder",
        "stations": [],
    })

