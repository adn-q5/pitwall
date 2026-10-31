import json
import sqlite3
import time
from pathlib import Path

# backend/cache/pitwall.db  (gitignored)
DEFAULT_PATH = Path(__file__).resolve().parents[2] / "cache" / "pitwall.db"


class Cache:
    """Tiny key-value cache on SQLite: key -> JSON response."""

    def __init__(self, path=DEFAULT_PATH):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS responses (
                key TEXT PRIMARY KEY,
                body TEXT NOT NULL,
                fetched_at REAL NOT NULL
            )"""
        )
        self.conn.commit()

    def get(self, key, ttl=None):
        """Return cached value, or None on a miss (or if older than ttl seconds)."""
        row = self.conn.execute(
            "SELECT body, fetched_at FROM responses WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        body, fetched_at = row
        if ttl is not None and time.time() - fetched_at > ttl:
            return None
        return json.loads(body)

    def set(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO responses (key, body, fetched_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time()),
        )
        self.conn.commit()