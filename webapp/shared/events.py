"""Event and attendance helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


def list_events(alliance_id: Optional[int] = None) -> List[Dict]:
    if alliance_id is None:
        return database.fetch_all("SELECT * FROM events ORDER BY start_time DESC")
    return database.fetch_all(
        "SELECT * FROM events WHERE alliance_id = ? ORDER BY start_time DESC",
        (alliance_id,),
    )


def create_event(name: str, start_time: str, *, description: Optional[str] = None, end_time: Optional[str] = None, reminder_minutes: int = 0, alliance_id: Optional[int] = None) -> int:
    return database.execute(
        """
        INSERT INTO events (name, description, start_time, end_time, reminder_minutes, alliance_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, description, start_time, end_time, reminder_minutes, alliance_id),
    )


def update_event(
    event_id: int,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    reminder_minutes: Optional[int] = None,
    alliance_id: Optional[int] = None,
) -> None:
    event = database.fetch_one("SELECT * FROM events WHERE id = ?", (event_id,))
    if not event:
        raise ValueError("Event not found")

    database.execute(
        """
        UPDATE events
        SET name = ?, description = ?, start_time = ?, end_time = ?, reminder_minutes = ?, alliance_id = ?
        WHERE id = ?
        """,
        (
            name if name is not None else event["name"],
            description if description is not None else event["description"],
            start_time if start_time is not None else event["start_time"],
            end_time if end_time is not None else event["end_time"],
            reminder_minutes if reminder_minutes is not None else event["reminder_minutes"],
            alliance_id if alliance_id is not None else event["alliance_id"],
            event_id,
        ),
    )


def delete_event(event_id: int) -> None:
    database.execute("DELETE FROM events WHERE id = ?", (event_id,))


def get_event(event_id: int) -> Optional[Dict]:
    return database.fetch_one("SELECT * FROM events WHERE id = ?", (event_id,))


__all__ = [
    "list_events",
    "create_event",
    "update_event",
    "delete_event",
    "get_event",
]
