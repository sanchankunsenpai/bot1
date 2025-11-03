"""Attendance tracking helpers."""

from __future__ import annotations

from typing import Dict, List

from . import database


def list_attendance(event_id: int) -> List[Dict]:
    return database.fetch_all(
        """
        SELECT ar.id, ar.event_id, ar.member_id, ar.status, ar.updated_at,
               m.name AS member_name, a.name AS alliance_name
        FROM attendance_records ar
        JOIN alliance_members m ON ar.member_id = m.id
        JOIN alliances a ON m.alliance_id = a.id
        WHERE ar.event_id = ?
        ORDER BY m.name
        """,
        (event_id,),
    )


def upsert_attendance(event_id: int, member_id: int, status: str) -> None:
    existing = database.fetch_one(
        "SELECT id FROM attendance_records WHERE event_id = ? AND member_id = ?",
        (event_id, member_id),
    )
    if existing:
        database.execute(
            "UPDATE attendance_records SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, existing["id"]),
        )
    else:
        database.execute(
            "INSERT INTO attendance_records (event_id, member_id, status) VALUES (?, ?, ?)",
            (event_id, member_id, status),
        )


def attendance_summary(alliance_id: int) -> List[Dict]:
    return database.fetch_all(
        """
        SELECT e.name AS event_name,
               SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) AS present,
               SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) AS absent,
               SUM(CASE WHEN ar.status = 'late' THEN 1 ELSE 0 END) AS late
        FROM events e
        LEFT JOIN attendance_records ar ON ar.event_id = e.id
        LEFT JOIN alliance_members m ON ar.member_id = m.id
        WHERE e.alliance_id = ?
        GROUP BY e.id
        ORDER BY e.start_time DESC
        """,
        (alliance_id,),
    )


__all__ = ["list_attendance", "upsert_attendance", "attendance_summary"]
