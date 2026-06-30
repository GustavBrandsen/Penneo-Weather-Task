"""
api.py - everything related to talking to the OpenWeather API.
"""
import requests

BASE_URL = "https://api.openweathermap.org/data/2.5/weather" # API info: https://openweathermap.org/api/current?collection=current_forecast#name


class WeatherAPIError(Exception):
    """Raised when the API call fails in a way we can't recover from."""


def fetch_weather(city: str, api_key: str, timeout: int = 10, retries: int = 3) -> dict:
    """
    Fetch current weather for a city and return the bits we care about:
    city name, temperature (Celsius), latitude, longitude.

    Retries on network errors / 5xx / 429 a few times with a short backoff,
    since those are often transient. Does NOT retry on 401 (bad key) or 404
    (unknown city) - those won't fix themselves.
    """
    params = {"q": city, "appid": api_key, "units": "metric"}

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=timeout)
        except requests.RequestException as exc:
            last_error = exc
            _wait_before_retry(attempt)
            continue

        if response.status_code == 401:
            raise WeatherAPIError("Invalid API key (401). Check OPENWEATHER_API_KEY in .env.")
        if response.status_code == 404:
            raise WeatherAPIError(f"City '{city}' not found (404).")
        if response.status_code in (429, 500, 502, 503, 504):
            last_error = WeatherAPIError(f"OpenWeather returned {response.status_code}, retrying...")
            _wait_before_retry(attempt)
            continue
        if not response.ok:
            raise WeatherAPIError(f"Unexpected status {response.status_code}: {response.text[:200]}")

        payload = response.json()
        try:
            return {
                "city": payload["name"] or city,
                "temperature_celsius": payload["main"]["temp"],
                "latitude": payload["coord"]["lat"],
                "longitude": payload["coord"]["lon"],
            }
        except KeyError as exc:
            raise WeatherAPIError(f"Unexpected response shape, missing field {exc}") from exc

    raise WeatherAPIError(f"Failed after {retries} attempts: {last_error}")


def _wait_before_retry(attempt: int) -> None:
    import time
    time.sleep(1.5 * attempt)  # 1.5s, 3s, 4.5s...
