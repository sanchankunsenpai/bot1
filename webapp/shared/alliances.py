"""Alliance and member management logic reused by the backend."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from . import database


# Alliance helpers ---------------------------------------------------------

def list_alliances() -> List[Dict]:
    return database.fetch_all(
        "SELECT id, name, discord_server_id, interval_minutes, created_at FROM alliances ORDER BY name"
    )


def get_alliance(alliance_id: int) -> Optional[Dict]:
    return database.fetch_one(
        "SELECT id, name, discord_server_id, interval_minutes, created_at FROM alliances WHERE id = ?",
        (alliance_id,),
    )


def create_alliance(name: str, discord_server_id: Optional[int], interval_minutes: int) -> int:
    return database.execute(
        "INSERT INTO alliances (name, discord_server_id, interval_minutes) VALUES (?, ?, ?)",
        (name, discord_server_id, interval_minutes),
    )


def update_alliance(
    alliance_id: int,
    *,
    name: Optional[str] = None,
    discord_server_id: Optional[int] = None,
    interval_minutes: Optional[int] = None,
) -> None:
    alliance = get_alliance(alliance_id)
    if not alliance:
        raise ValueError("Alliance not found")

    name = name if name is not None else alliance["name"]
    discord_server_id = (
        discord_server_id if discord_server_id is not None else alliance["discord_server_id"]
    )
    interval_minutes = (
        interval_minutes if interval_minutes is not None else alliance["interval_minutes"]
    )

    database.execute(
        "UPDATE alliances SET name = ?, discord_server_id = ?, interval_minutes = ? WHERE id = ?",
        (name, discord_server_id, interval_minutes, alliance_id),
    )


def delete_alliance(alliance_id: int) -> None:
    database.execute("DELETE FROM alliances WHERE id = ?", (alliance_id,))


# Member helpers -----------------------------------------------------------

def list_members(alliance_id: Optional[int] = None) -> List[Dict]:
    if alliance_id is None:
        return database.fetch_all(
            """
            SELECT m.id, m.alliance_id, m.name, m.fl_level, m.title, m.joined_at, m.notes,
                   a.name AS alliance_name
            FROM alliance_members m
            LEFT JOIN alliances a ON m.alliance_id = a.id
            ORDER BY a.name, m.name
            """
        )
    return database.fetch_all(
        """
        SELECT m.id, m.alliance_id, m.name, m.fl_level, m.title, m.joined_at, m.notes,
               a.name AS alliance_name
        FROM alliance_members m
        LEFT JOIN alliances a ON m.alliance_id = a.id
        WHERE m.alliance_id = ?
        ORDER BY m.name
        """,
        (alliance_id,),
    )


def add_member(
    alliance_id: int,
    name: str,
    *,
    fl_level: Optional[int] = None,
    title: Optional[str] = None,
    joined_at: Optional[str] = None,
    notes: Optional[str] = None,
) -> int:
    return database.execute(
        """
        INSERT INTO alliance_members (alliance_id, name, fl_level, title, joined_at, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (alliance_id, name, fl_level, title, joined_at, notes),
    )


def update_member(
    member_id: int,
    *,
    name: Optional[str] = None,
    fl_level: Optional[int] = None,
    title: Optional[str] = None,
    joined_at: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    member = database.fetch_one("SELECT * FROM alliance_members WHERE id = ?", (member_id,))
    if not member:
        raise ValueError("Member not found")

    database.execute(
        """
        UPDATE alliance_members
        SET name = ?, fl_level = ?, title = ?, joined_at = ?, notes = ?
        WHERE id = ?
        """,
        (
            name if name is not None else member["name"],
            fl_level if fl_level is not None else member["fl_level"],
            title if title is not None else member["title"],
            joined_at if joined_at is not None else member["joined_at"],
            notes if notes is not None else member["notes"],
            member_id,
        ),
    )


def remove_member(member_id: int) -> None:
    database.execute("DELETE FROM alliance_members WHERE id = ?", (member_id,))


__all__ = [
    "list_alliances",
    "get_alliance",
    "create_alliance",
    "update_alliance",
    "delete_alliance",
    "list_members",
    "add_member",
    "update_member",
    "remove_member",
]
