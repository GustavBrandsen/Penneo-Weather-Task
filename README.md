# Take-Home Weather Assignment for Penneo

Fetch OpenWeather every minute for a city's temperature and saves it to SQLite.

## Files

- **`api.py`** — talks to OpenWeather. One function, `fetch_weather()`, with
  retries on transient errors (network issues, 429, 5xx) and fail-fast on
  permanent ones (bad API key, unknown city).
- **`storage.py`** — the dataset. SQLite table with city, lat/lon, temperature,
  timestamp. `save_reading()` and `get_latest()`.
- **`main.py`** — glues them together: a loop that fetches and saves once a
  minute, with basic logging and error handling so one bad fetch doesn't
  kill the process.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OpenWeather API key
python main.py
```

Check the data:

```bash
sqlite3 weather.db "SELECT * FROM weather_readings ORDER BY fetched_at DESC LIMIT 5;"
```

## Key decisions

- **SQLite**: zero setup, fine for one write/minute. `storage.py` is the only
  file that knows about the database, so it's easy to swap later.
- **No scheduling library**: a `while True` + `time.sleep()` loop is enough
  for "every 60 seconds"; subtracting elapsed time from the sleep keeps it
  roughly on cadence even if the API is slow to respond.
- **Retries**: only on transient failures (network, 429, 5xx). A bad API key
  or unknown city won't fix itself, so those raise immediately instead of
  wasting retry attempts.
- **API key**: read from an environment variable (`.env`, gitignored), never
  hardcoded or logged.
