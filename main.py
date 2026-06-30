"""
main.py - runs the poll loop: fetch weather every minute, save it.

Config is just a couple of env vars (set them or use the defaults below).
"""
import logging
import os
import time

from dotenv import load_dotenv

from api import fetch_weather, WeatherAPIError
from storage import init_db, save_reading

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
CITY = os.environ.get("WEATHER_CITY", "Copenhagen,DK")
INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "60"))


def main() -> None:
    if not API_KEY:
        raise SystemExit("Missing OPENWEATHER_API_KEY in .env.")

    init_db()
    logger.info("Starting poller for city=%s every %ss", CITY, INTERVAL_SECONDS)

    while True:
        start = time.monotonic()
        try:
            reading = fetch_weather(CITY, API_KEY)
            save_reading(reading)
            logger.info("Saved: %s %.1fC", reading["city"], reading["temperature_celsius"])
        except WeatherAPIError as exc:
            logger.error("Fetch failed, will try again next interval: %s", exc)
        except Exception:
            logger.exception("Unexpected error")

        elapsed = time.monotonic() - start
        time.sleep(max(0, INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    main()
