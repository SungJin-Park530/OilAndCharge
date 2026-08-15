from flask import Blueprint, jsonify


fuel_bp = Blueprint("fuel", __name__, url_prefix="/fuel")


@fuel_bp.route("/")
def index():
    return jsonify({
        "message": "Fuel API is running",
        "routes": [
            "/fuel",
            "/fuel/stations",
        ],
    })


@fuel_bp.route("/stations")
def stations():
    return jsonify({
        "message": "Station list placeholder",
        "stations": [],
    })
