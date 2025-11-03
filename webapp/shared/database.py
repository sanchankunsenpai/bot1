"""Database helpers shared between the backend routers."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

DB_DIR = Path("db")
DEFAULT_DB_PATH = DB_DIR / "webapp.sqlite"


def ensure_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the SQLite database and required tables if they do not exist."""

    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS alliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                discord_server_id INTEGER,
                interval_minutes INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS alliance_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alliance_id INTEGER NOT NULL REFERENCES alliances(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                fl_level INTEGER,
                title TEXT,
                joined_at TEXT,
                notes TEXT,
                UNIQUE(alliance_id, name)
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                reminder_minutes INTEGER DEFAULT 0,
                alliance_id INTEGER REFERENCES alliances(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                member_id INTEGER NOT NULL REFERENCES alliance_members(id) ON DELETE CASCADE,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, member_id)
            );

            CREATE TABLE IF NOT EXISTS ministers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alliance_id INTEGER REFERENCES alliances(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                player_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS gift_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                alliance_id INTEGER REFERENCES alliances(id) ON DELETE SET NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                redeemed_by TEXT,
                redeemed_at TEXT,
                validation_status TEXT NOT NULL DEFAULT 'pending',
                last_checked_at TEXT,
                confidence REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Backward compatibility for previous databases that may miss new columns
        existing_columns = {
            row[1]: True
            for row in conn.execute("PRAGMA table_info(gift_codes)")
        }
        if "created_at" not in existing_columns:
            conn.execute(
                "ALTER TABLE gift_codes ADD COLUMN created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
            )


@contextmanager
def get_connection(db_path: Path = DEFAULT_DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    ensure_database(db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def fetch_all(query: str, params: Iterable = (), db_path: Path = DEFAULT_DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def fetch_one(query: str, params: Iterable = (), db_path: Path = DEFAULT_DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute(query: str, params: Iterable = (), db_path: Path = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(query, params)
        return cur.lastrowid


def executemany(query: str, seq_of_params: Iterable[Iterable], db_path: Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executemany(query, seq_of_params)


__all__ = [
    "ensure_database",
    "get_connection",
    "fetch_all",
    "fetch_one",
    "execute",
    "executemany",
]
