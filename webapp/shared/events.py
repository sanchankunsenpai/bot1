"""Event and attendance helpers."""

from __future__ import annotations

from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from . import database


def list_events(alliance_id: Optional[int] = None) -> List[Dict]:
    params: List[str] = []
    where_clause = ""
    if alliance_id is not None:
        where_clause = "WHERE alliance_id = ?"
        params.append(str(alliance_id))

    query = f"""
        SELECT session_id,
               MAX(session_name) AS session_name,
               MAX(event_type) AS event_type,
               MAX(event_date) AS event_date,
               MAX(alliance_id) AS alliance_id,
               MAX(alliance_name) AS alliance_name
        FROM attendance_records
        {where_clause}
        GROUP BY session_id
        ORDER BY MAX(event_date) DESC
    """

    sessions = database.fetch_all(
        query,
        params,
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )

    metadata_rows = database.fetch_all(
        "SELECT session_id, description, end_time, reminder_minutes FROM events_metadata",
        db_path=database.WEBAPP_DB_PATH,
        ensure=database.ensure_webapp_schema,
    )
    metadata = {row["session_id"]: row for row in metadata_rows}

    results: List[Dict] = []
    for session in sessions:
        alliance_value = session.get("alliance_id")
        item = {
            "id": session["session_id"],
            "name": session["session_name"],
            "event_type": session["event_type"],
            "event_date": session["event_date"],
            "alliance_id": int(alliance_value) if alliance_value is not None else None,
            "alliance_name": session["alliance_name"],
        }
        meta = metadata.get(session["session_id"])
        if meta:
            item["description"] = meta.get("description")
            item["end_time"] = meta.get("end_time")
            item["reminder_minutes"] = meta.get("reminder_minutes")
        else:
            item["description"] = None
            item["end_time"] = None
            item["reminder_minutes"] = 0
        results.append(item)

    return results


def _fetch_alliance(alliance_id: int) -> Dict:
    alliance = database.fetch_one(
        "SELECT alliance_id, name FROM alliance_list WHERE alliance_id = ?",
        (alliance_id,),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    if alliance is None:
        raise ValueError("Alliance not found")
    return alliance


def create_event(
    name: str,
    start_time: str,
    *,
    description: Optional[str] = None,
    end_time: Optional[str] = None,
    reminder_minutes: int = 0,
    alliance_id: Optional[int] = None,
) -> str:
    if alliance_id is None:
        raise ValueError("Alliance ID is required to create attendance sessions")

    alliance = _fetch_alliance(alliance_id)
    members = database.fetch_all(
        """
        SELECT fid, nickname FROM users
        WHERE alliance = ? OR alliance = ?
        ORDER BY nickname
        """,
        (alliance_id, str(alliance_id)),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )

    session_id = uuid.uuid4().hex
    attendance_rows = [
        (
            str(member["fid"]),
            member["nickname"],
            session_id,
            name,
            str(alliance["alliance_id"]),
            alliance["name"],
            "not_recorded",
            0,
            description or "General",
            start_time,
            "webapp",
            "Control Center",
        )
        for member in members
    ]

    if attendance_rows:
        database.executemany(
            """
            INSERT INTO attendance_records
            (player_id, player_name, session_id, session_name, alliance_id, alliance_name,
             status, points, event_type, event_date, marked_by, marked_by_username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            attendance_rows,
            db_path=database.ATTENDANCE_DB_PATH,
            ensure=database.ensure_attendance_schema,
        )

    database.execute(
        """
        INSERT INTO events_metadata (session_id, description, end_time, reminder_minutes, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            description = excluded.description,
            end_time = excluded.end_time,
            reminder_minutes = excluded.reminder_minutes,
            updated_at = CURRENT_TIMESTAMP
        """,
        (session_id, description, end_time, reminder_minutes),
        db_path=database.WEBAPP_DB_PATH,
        ensure=database.ensure_webapp_schema,
    )

    return session_id


def update_event(
    session_id: str,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    reminder_minutes: Optional[int] = None,
) -> None:
    event = get_event(session_id)
    if event is None:
        raise ValueError("Event not found")

    database.execute(
        """
        UPDATE attendance_records
        SET session_name = ?, event_type = ?, event_date = ?
        WHERE session_id = ?
        """,
        (
            name if name is not None else event["name"],
            description if description is not None else event.get("event_type"),
            start_time if start_time is not None else event.get("event_date"),
            session_id,
        ),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )

    database.execute(
        """
        INSERT INTO events_metadata (session_id, description, end_time, reminder_minutes, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            description = excluded.description,
            end_time = excluded.end_time,
            reminder_minutes = excluded.reminder_minutes,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            session_id,
            description if description is not None else event.get("description"),
            end_time if end_time is not None else event.get("end_time"),
            reminder_minutes if reminder_minutes is not None else event.get("reminder_minutes", 0),
        ),
        db_path=database.WEBAPP_DB_PATH,
        ensure=database.ensure_webapp_schema,
    )


def delete_event(session_id: str) -> None:
    database.execute(
        "DELETE FROM attendance_records WHERE session_id = ?",
        (session_id,),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )
    database.execute(
        "DELETE FROM events_metadata WHERE session_id = ?",
        (session_id,),
        db_path=database.WEBAPP_DB_PATH,
        ensure=database.ensure_webapp_schema,
    )


def get_event(session_id: str) -> Optional[Dict]:
    events = list_events()
    for item in events:
        if item["id"] == session_id:
            return item
    return None


__all__ = [
    "list_events",
    "create_event",
    "update_event",
    "delete_event",
    "get_event",
]
