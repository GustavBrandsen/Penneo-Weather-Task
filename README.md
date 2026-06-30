# Take-Home Weather Assignment for Penneo

This project gets the temperature for Copenhagen from OpenWeather once every minute and stores it in a local SQLite database.

## Files

- **`api.py`**
  Calls OpenWeather and returns the weather data.
  If there is a temporary problem (like network issues), it retries.
  If the problem is permanent (like wrong API key), it stops right away.
- **`storage.py`**
  Handles the SQLite database.
  Creates/saves rows with city, coordinates, temperature, and timestamp.
  Main functions: `save_reading()` and `get_latest()`.
- **`main.py`**
  Runs the app loop.
  Every minute it fetches data from `api.py` and saves it using `storage.py`.
  Includes basic logging and error handling so one failed request does not stop the app.

## Run it

```bash
pip install -r requirements.txt
python main.py
```
> Before running, open '.env' and add your OpenWeather API key

Check the data:

```bash
sqlite3 weather.db "SELECT * FROM weather_readings ORDER BY fetched_at DESC LIMIT 5;"
```

## Key decisions

- **SQLite**
  Easy to use, no extra setup, and enough for one write per minute.
  Only `storage.py` knows about database details, so changing database later is easier.
- **No scheduler package**
  A simple `while True` + `time.sleep()` loop is enough for "run every 60 seconds".
  The code adjusts sleep time based on how long the request took.
- **Retries only for temporary errors**
  Retries for network errors, rate limits (429), and server errors (5xx).
  It does not retry invalid API keys or unknown cities.
- **API key from environment**
  The key comes from `.env` and is never hardcoded.
