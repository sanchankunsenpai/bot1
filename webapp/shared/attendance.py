"""Attendance tracking helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


def list_attendance(session_id: str) -> List[Dict]:
    session_key = str(session_id)
    return database.fetch_all(
        """
        SELECT
            record_id AS id,
            session_id,
            session_name,
            player_id,
            player_name,
            alliance_id,
            alliance_name,
            status,
            points,
            event_type,
            event_date,
            marked_at,
            marked_by,
            marked_by_username
        FROM attendance_records
        WHERE session_id = ?
        ORDER BY player_name COLLATE NOCASE
        """,
        (session_key,),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )


def _fetch_session_template(session_id: str) -> Optional[Dict]:
    return database.fetch_one(
        """
        SELECT session_name, alliance_id, alliance_name, event_type, event_date
        FROM attendance_records
        WHERE session_id = ?
        LIMIT 1
        """,
        (session_id,),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )


def upsert_attendance(session_id: str, member_id: int, status: str) -> None:
    session_key = str(session_id)
    player_id = str(member_id)
    existing = database.fetch_one(
        "SELECT record_id FROM attendance_records WHERE session_id = ? AND player_id = ?",
        (session_key, player_id),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )
    if existing:
        database.execute(
            """
            UPDATE attendance_records
            SET status = ?, marked_at = CURRENT_TIMESTAMP
            WHERE record_id = ?
            """,
            (status, existing["record_id"]),
            db_path=database.ATTENDANCE_DB_PATH,
            ensure=database.ensure_attendance_schema,
        )
        return

    template = _fetch_session_template(session_key)
    if template is None:
        raise ValueError("Attendance session not found")

    database.execute(
        """
        INSERT INTO attendance_records (
            player_id,
            player_name,
            session_id,
            session_name,
            alliance_id,
            alliance_name,
            status,
            points,
            event_type,
            event_date,
            marked_by,
            marked_by_username
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 'webapp', 'Control Center')
        """,
        (
            player_id,
            player_id,
            session_key,
            template["session_name"],
            template["alliance_id"],
            template["alliance_name"],
            status,
            template.get("event_type"),
            template.get("event_date"),
        ),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )


def attendance_summary(alliance_id: int) -> List[Dict]:
    alliance_key = str(alliance_id)
    return database.fetch_all(
        """
        SELECT
            session_name AS event_name,
            SUM(CASE WHEN LOWER(status) = 'present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN LOWER(status) = 'absent' THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN LOWER(status) = 'late' THEN 1 ELSE 0 END) AS late,
            MAX(event_date) AS last_event_date
        FROM attendance_records
        WHERE alliance_id = ?
        GROUP BY session_id, session_name
        ORDER BY last_event_date DESC
        """,
        (alliance_key,),
        db_path=database.ATTENDANCE_DB_PATH,
        ensure=database.ensure_attendance_schema,
    )


__all__ = ["list_attendance", "upsert_attendance", "attendance_summary"]
