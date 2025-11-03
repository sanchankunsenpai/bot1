"""Database helpers shared between the backend routers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Generator, Iterable, Optional

DB_DIR = Path("db")

# Paths that mirror the Discord bot layout -----------------------------------
WEBAPP_DB_PATH = DB_DIR / "webapp.sqlite"
ALLIANCE_DB_PATH = DB_DIR / "alliance.sqlite"
USERS_DB_PATH = DB_DIR / "users.sqlite"
GIFTCODE_DB_PATH = DB_DIR / "giftcode.sqlite"
ATTENDANCE_DB_PATH = DB_DIR / "attendance.sqlite"
SVS_DB_PATH = DB_DIR / "svs.sqlite"
SETTINGS_DB_PATH = DB_DIR / "settings.sqlite"


def _create_dir() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)


def ensure_webapp_schema() -> None:
    """Create tables that only the web control centre needs."""

    _create_dir()
    with sqlite3.connect(WEBAPP_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
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

            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS events_metadata (
                session_id TEXT PRIMARY KEY,
                description TEXT,
                end_time TEXT,
                reminder_minutes INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def ensure_alliance_schema() -> None:
    """Ensure the alliance database mirrors the Discord bot schema."""

    _create_dir()
    with sqlite3.connect(ALLIANCE_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS alliance_list (
                alliance_id INTEGER PRIMARY KEY,
                name TEXT,
                discord_server_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS alliancesettings (
                alliance_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                interval INTEGER
            );
            """
        )

        columns = [row[1] for row in conn.execute("PRAGMA table_info(alliance_list)")]
        if "discord_server_id" not in columns:
            conn.execute("ALTER TABLE alliance_list ADD COLUMN discord_server_id INTEGER")


def ensure_users_schema() -> None:
    """Ensure the member roster database exists."""

    _create_dir()
    with sqlite3.connect(USERS_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                fid INTEGER PRIMARY KEY,
                nickname TEXT,
                furnace_lv INTEGER DEFAULT 0,
                kid INTEGER,
                stove_lv_content TEXT,
                alliance TEXT
            );
            """
        )


def ensure_giftcode_schema() -> None:
    """Ensure the gift code database matches the bot expectations."""

    _create_dir()
    with sqlite3.connect(GIFTCODE_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS gift_codes (
                giftcode TEXT PRIMARY KEY,
                date TEXT,
                alliance_id INTEGER,
                validation_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_giftcodes (
                fid INTEGER,
                giftcode TEXT,
                status TEXT,
                PRIMARY KEY (fid, giftcode),
                FOREIGN KEY (giftcode) REFERENCES gift_codes (giftcode)
            );

            CREATE TABLE IF NOT EXISTS giftcodecontrol (
                alliance_id INTEGER PRIMARY KEY,
                status INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS giftcode_channel (
                alliance_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                scan_history INTEGER DEFAULT 0
            );
            """
        )

        columns = [row[1] for row in conn.execute("PRAGMA table_info(gift_codes)")]
        if "validation_status" not in columns:
            conn.execute(
                "ALTER TABLE gift_codes ADD COLUMN validation_status TEXT DEFAULT 'pending'"
            )
        if "alliance_id" not in columns:
            conn.execute("ALTER TABLE gift_codes ADD COLUMN alliance_id INTEGER")
        if "created_at" not in columns:
            conn.execute(
                "ALTER TABLE gift_codes ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            )


def ensure_attendance_schema() -> None:
    """Ensure the attendance database mirrors the bot layout."""

    _create_dir()
    with sqlite3.connect(ATTENDANCE_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                session_name TEXT NOT NULL,
                event_type TEXT NOT NULL DEFAULT 'Other',
                event_date TEXT,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                alliance_id TEXT NOT NULL,
                alliance_name TEXT NOT NULL,
                status TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                marked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                marked_by TEXT,
                marked_by_username TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, player_id)
            );
            """
        )


def ensure_svs_schema() -> None:
    """Ensure the minister scheduling database exists."""

    _create_dir()
    with sqlite3.connect(SVS_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                fid INTEGER,
                appointment_type TEXT,
                time TEXT,
                alliance INTEGER,
                PRIMARY KEY (fid, appointment_type)
            );

            CREATE TABLE IF NOT EXISTS reference (
                context TEXT PRIMARY KEY,
                context_id INTEGER
            );
            """
        )


def ensure_settings_schema() -> None:
    """Ensure the settings database exists so joins can resolve."""

    _create_dir()
    with sqlite3.connect(SETTINGS_DB_PATH, timeout=30.0) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS botsettings (
                id INTEGER PRIMARY KEY,
                channelid INTEGER,
                giftcodestatus TEXT
            );

            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY,
                is_initial INTEGER
            );
            """
        )


EnsureCallback = Optional[Callable[[], None]]


@contextmanager
def get_connection(db_path: Path, ensure: EnsureCallback = None) -> Generator[sqlite3.Connection, None, None]:
    if ensure is not None:
        ensure()
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def fetch_all(
    query: str,
    params: Iterable = (),
    *,
    db_path: Path = WEBAPP_DB_PATH,
    ensure: EnsureCallback = None,
):
    with get_connection(db_path, ensure=ensure) as conn:
        cur = conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def fetch_one(
    query: str,
    params: Iterable = (),
    *,
    db_path: Path = WEBAPP_DB_PATH,
    ensure: EnsureCallback = None,
):
    with get_connection(db_path, ensure=ensure) as conn:
        cur = conn.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute(
    query: str,
    params: Iterable = (),
    *,
    db_path: Path = WEBAPP_DB_PATH,
    ensure: EnsureCallback = None,
) -> int:
    with get_connection(db_path, ensure=ensure) as conn:
        cur = conn.execute(query, params)
        return cur.lastrowid


def executemany(
    query: str,
    seq_of_params: Iterable[Iterable],
    *,
    db_path: Path = WEBAPP_DB_PATH,
    ensure: EnsureCallback = None,
) -> None:
    with get_connection(db_path, ensure=ensure) as conn:
        conn.executemany(query, seq_of_params)


__all__ = [
    "ATTENDANCE_DB_PATH",
    "ALLIANCE_DB_PATH",
    "GIFTCODE_DB_PATH",
    "SETTINGS_DB_PATH",
    "SVS_DB_PATH",
    "USERS_DB_PATH",
    "WEBAPP_DB_PATH",
    "ensure_alliance_schema",
    "ensure_attendance_schema",
    "ensure_giftcode_schema",
    "ensure_settings_schema",
    "ensure_svs_schema",
    "ensure_users_schema",
    "ensure_webapp_schema",
    "executemany",
    "execute",
    "fetch_all",
    "fetch_one",
    "get_connection",
]
