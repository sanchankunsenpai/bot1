"""Minister schedule helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


def _to_int(value) -> Optional[int]:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def list_ministers(alliance_id: Optional[int] = None) -> List[Dict]:
    if alliance_id is None:
        rows = database.fetch_all(
            "SELECT fid, appointment_type, time, alliance FROM appointments ORDER BY time DESC",
            db_path=database.SVS_DB_PATH,
            ensure=database.ensure_svs_schema,
        )
    else:
        rows = database.fetch_all(
            "SELECT fid, appointment_type, time, alliance FROM appointments WHERE alliance = ? ORDER BY time DESC",
            (int(alliance_id),),
            db_path=database.SVS_DB_PATH,
            ensure=database.ensure_svs_schema,
        )

    names = database.fetch_all(
        "SELECT fid, nickname FROM users",
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )
    name_lookup = {row["fid"]: row["nickname"] for row in names}

    for row in rows:
        row["player_name"] = name_lookup.get(row["fid"])
        alliance_value = row.get("alliance")
        row["alliance_id"] = _to_int(alliance_value)
        row["id"] = f"{row['fid']}:{row['appointment_type']}"
    return rows


def create_minister(
    fid: int,
    appointment_type: str,
    time: str,
    alliance_id: Optional[int],
) -> None:
    database.execute(
        """
        INSERT OR REPLACE INTO appointments (fid, appointment_type, time, alliance)
        VALUES (?, ?, ?, ?)
        """,
        (fid, appointment_type, time, _to_int(alliance_id) if alliance_id is not None else None),
        db_path=database.SVS_DB_PATH,
        ensure=database.ensure_svs_schema,
    )


def update_minister(
    fid: int,
    appointment_type: str,
    *,
    time: Optional[str] = None,
    alliance_id: Optional[int] = None,
) -> None:
    record = database.fetch_one(
        "SELECT fid, appointment_type, time, alliance FROM appointments WHERE fid = ? AND appointment_type = ?",
        (fid, appointment_type),
        db_path=database.SVS_DB_PATH,
        ensure=database.ensure_svs_schema,
    )
    if record is None:
        raise ValueError("Minister booking not found")

    database.execute(
        """
        UPDATE appointments
        SET time = ?, alliance = ?
        WHERE fid = ? AND appointment_type = ?
        """,
        (
            time if time is not None else record["time"],
            _to_int(alliance_id) if alliance_id is not None else record.get("alliance"),
            fid,
            appointment_type,
        ),
        db_path=database.SVS_DB_PATH,
        ensure=database.ensure_svs_schema,
    )


def delete_minister(fid: int, appointment_type: str) -> None:
    database.execute(
        "DELETE FROM appointments WHERE fid = ? AND appointment_type = ?",
        (fid, appointment_type),
        db_path=database.SVS_DB_PATH,
        ensure=database.ensure_svs_schema,
    )


__all__ = [
    "list_ministers",
    "create_minister",
    "update_minister",
    "delete_minister",
]
