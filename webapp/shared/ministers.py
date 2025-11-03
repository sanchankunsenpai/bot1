"""Minister schedule helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


def list_ministers(alliance_id: Optional[int] = None) -> List[Dict]:
    if alliance_id is None:
        return database.fetch_all("SELECT * FROM ministers ORDER BY start_time DESC")
    return database.fetch_all(
        "SELECT * FROM ministers WHERE alliance_id = ? ORDER BY start_time DESC",
        (alliance_id,),
    )


def create_minister(
    alliance_id: Optional[int],
    role: str,
    player_name: str,
    start_time: str,
    end_time: str,
    *,
    notes: Optional[str] = None,
) -> int:
    return database.execute(
        """
        INSERT INTO ministers (alliance_id, role, player_name, start_time, end_time, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (alliance_id, role, player_name, start_time, end_time, notes),
    )


def update_minister(
    minister_id: int,
    *,
    alliance_id: Optional[int] = None,
    role: Optional[str] = None,
    player_name: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    minister = database.fetch_one("SELECT * FROM ministers WHERE id = ?", (minister_id,))
    if not minister:
        raise ValueError("Minister booking not found")

    database.execute(
        """
        UPDATE ministers
        SET alliance_id = ?, role = ?, player_name = ?, start_time = ?, end_time = ?, notes = ?
        WHERE id = ?
        """,
        (
            alliance_id if alliance_id is not None else minister["alliance_id"],
            role if role is not None else minister["role"],
            player_name if player_name is not None else minister["player_name"],
            start_time if start_time is not None else minister["start_time"],
            end_time if end_time is not None else minister["end_time"],
            notes if notes is not None else minister["notes"],
            minister_id,
        ),
    )


def delete_minister(minister_id: int) -> None:
    database.execute("DELETE FROM ministers WHERE id = ?", (minister_id,))


__all__ = [
    "list_ministers",
    "create_minister",
    "update_minister",
    "delete_minister",
]
