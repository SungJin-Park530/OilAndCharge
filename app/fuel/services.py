import os

import requests


OPINET_BASE_URL = "https://www.opinet.co.kr/api"


def get_opinet_api_key() -> str:
    return os.getenv("OPINET_API_KEY", "")


def fetch_station_data() -> dict:
    api_key = get_opinet_api_key()
    if not api_key:
        return {"error": "OPINET_API_KEY is not set"}

    try:
        response = requests.get(
            f"{OPINET_BASE_URL}/details",
            params={"apiKey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}
