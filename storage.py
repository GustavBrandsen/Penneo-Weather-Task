"""
storage.py - everything related to persisting weather readings.

Uses SQLite: a single file, no server to run, good enough for one write a
minute. Swap this module out if you ever need a different database - the
rest of the code just calls save_reading() / get_latest().
"""
import sqlite3
from datetime import datetime, timezone

DB_PATH = "weather.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    temperature_celsius REAL NOT NULL,
    fetched_at TEXT NOT NULL
);
"""


def init_db(db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(SCHEMA)


def save_reading(reading: dict, db_path: str = DB_PATH) -> None:
    """reading: dict with city, temperature_celsius, latitude, longitude."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO weather_readings (city, latitude, longitude, temperature_celsius, fetched_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reading["city"],
                reading["latitude"],
                reading["longitude"],
                reading["temperature_celsius"],
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def get_latest(limit: int = 10, db_path: str = DB_PATH) -> list[sqlite3.Row]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM weather_readings ORDER BY fetched_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return rows
