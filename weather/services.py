import requests


def fetch_air_temperature_data():
    url = "https://api.data.gov.sg/v1/environment/air-temperature"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching air temperature data: {e}")
        return None
