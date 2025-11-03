"""Alliance and member management logic reused by the backend."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


# Alliance helpers ---------------------------------------------------------


def _to_int(value) -> Optional[int]:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _alliances_lookup() -> Dict[int, str]:
    rows = database.fetch_all(
        "SELECT alliance_id, name FROM alliance_list ORDER BY alliance_id",
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    result: Dict[int, str] = {}
    for row in rows:
        key = _to_int(row.get("alliance_id"))
        if key is not None:
            result[key] = row.get("name")
    return result


def list_alliances() -> List[Dict]:
    rows = database.fetch_all(
        """
        SELECT
            a.alliance_id AS id,
            a.name,
            a.discord_server_id,
            COALESCE(s.interval, 0) AS interval_minutes,
            s.channel_id
        FROM alliance_list a
        LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
        ORDER BY a.alliance_id ASC
        """,
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )

    counts: Dict[int, int] = {}
    member_rows = database.fetch_all(
        "SELECT alliance, COUNT(*) AS total FROM users GROUP BY alliance",
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )
    for entry in member_rows:
        key = _to_int(entry.get("alliance"))
        if key is not None:
            counts[key] = entry["total"]

    for row in rows:
        row_id = _to_int(row.get("id"))
        row["member_count"] = counts.get(row_id, 0) if row_id is not None else 0

    return rows


def get_alliance(alliance_id: int) -> Optional[Dict]:
    alliance = database.fetch_one(
        """
        SELECT
            a.alliance_id AS id,
            a.name,
            a.discord_server_id,
            COALESCE(s.interval, 0) AS interval_minutes,
            s.channel_id
        FROM alliance_list a
        LEFT JOIN alliancesettings s ON a.alliance_id = s.alliance_id
        WHERE a.alliance_id = ?
        """,
        (alliance_id,),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    if alliance:
        member_count = database.fetch_one(
            "SELECT COUNT(*) AS total FROM users WHERE alliance = ? OR alliance = ?",
            (alliance_id, str(alliance_id)),
            db_path=database.USERS_DB_PATH,
            ensure=database.ensure_users_schema,
        )
        alliance["member_count"] = member_count["total"] if member_count else 0
    return alliance


def create_alliance(
    name: str,
    discord_server_id: Optional[int],
    interval_minutes: int,
    *,
    channel_id: Optional[int] = None,
) -> int:
    alliance_id = database.execute(
        "INSERT INTO alliance_list (name, discord_server_id) VALUES (?, ?)",
        (name, discord_server_id),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    database.execute(
        """
        INSERT INTO alliancesettings (alliance_id, channel_id, interval)
        VALUES (?, ?, ?)
        ON CONFLICT(alliance_id) DO UPDATE SET
            channel_id = excluded.channel_id,
            interval = excluded.interval
        """,
        (alliance_id, channel_id, interval_minutes),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    return alliance_id


def update_alliance(
    alliance_id: int,
    *,
    name: Optional[str] = None,
    discord_server_id: Optional[int] = None,
    interval_minutes: Optional[int] = None,
    channel_id: Optional[int] = None,
) -> None:
    alliance = get_alliance(alliance_id)
    if alliance is None:
        raise ValueError("Alliance not found")

    database.execute(
        "UPDATE alliance_list SET name = ?, discord_server_id = ? WHERE alliance_id = ?",
        (
            name if name is not None else alliance["name"],
            discord_server_id
            if discord_server_id is not None
            else alliance.get("discord_server_id"),
            alliance_id,
        ),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )

    database.execute(
        """
        INSERT INTO alliancesettings (alliance_id, channel_id, interval)
        VALUES (?, ?, ?)
        ON CONFLICT(alliance_id) DO UPDATE SET
            channel_id = excluded.channel_id,
            interval = excluded.interval
        """,
        (
            alliance_id,
            channel_id if channel_id is not None else alliance.get("channel_id"),
            interval_minutes
            if interval_minutes is not None
            else alliance.get("interval_minutes", 0),
        ),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )


def delete_alliance(alliance_id: int) -> None:
    database.execute(
        "DELETE FROM alliancesettings WHERE alliance_id = ?",
        (alliance_id,),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    database.execute(
        "DELETE FROM alliance_list WHERE alliance_id = ?",
        (alliance_id,),
        db_path=database.ALLIANCE_DB_PATH,
        ensure=database.ensure_alliance_schema,
    )
    database.execute(
        "UPDATE users SET alliance = NULL WHERE alliance = ? OR alliance = ?",
        (alliance_id, str(alliance_id)),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )


# Member helpers -----------------------------------------------------------


def list_members(alliance_id: Optional[int] = None) -> List[Dict]:
    alliances = _alliances_lookup()

    if alliance_id is None:
        members = database.fetch_all(
            "SELECT fid, nickname, furnace_lv, kid, stove_lv_content, alliance FROM users ORDER BY nickname",
            db_path=database.USERS_DB_PATH,
            ensure=database.ensure_users_schema,
        )
    else:
        members = database.fetch_all(
            """
            SELECT fid, nickname, furnace_lv, kid, stove_lv_content, alliance
            FROM users
            WHERE alliance = ? OR alliance = ?
            ORDER BY nickname
            """,
            (alliance_id, str(alliance_id)),
            db_path=database.USERS_DB_PATH,
            ensure=database.ensure_users_schema,
        )

    for member in members:
        alliance_value = member.get("alliance")
        alliance_int = _to_int(alliance_value)
        member["alliance_id"] = alliance_int
        member["alliance_name"] = alliances.get(alliance_int) if alliance_int is not None else None
    return members


def _next_member_id() -> int:
    row = database.fetch_one(
        "SELECT COALESCE(MAX(fid), 0) + 1 AS next_id FROM users",
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )
    return int(row["next_id"]) if row and row.get("next_id") is not None else 1


def add_member(
    fid: Optional[int],
    nickname: str,
    *,
    alliance_id: Optional[int] = None,
    furnace_lv: Optional[int] = None,
    kid: Optional[int] = None,
    stove_lv_content: Optional[str] = None,
) -> int:
    if fid is None:
        fid = _next_member_id()

    database.execute(
        """
        INSERT INTO users (fid, nickname, furnace_lv, kid, stove_lv_content, alliance)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            fid,
            nickname,
            furnace_lv,
            kid,
            stove_lv_content,
            alliance_id if alliance_id is not None else None,
        ),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )
    return fid


def update_member(
    fid: int,
    *,
    nickname: Optional[str] = None,
    furnace_lv: Optional[int] = None,
    kid: Optional[int] = None,
    stove_lv_content: Optional[str] = None,
    alliance_id: Optional[int] = None,
) -> None:
    member = database.fetch_one(
        "SELECT * FROM users WHERE fid = ?",
        (fid,),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )
    if member is None:
        raise ValueError("Member not found")

    existing_alliance = _to_int(member.get("alliance"))
    next_alliance = alliance_id if alliance_id is not None else existing_alliance

    database.execute(
        """
        UPDATE users
        SET nickname = ?, furnace_lv = ?, kid = ?, stove_lv_content = ?, alliance = ?
        WHERE fid = ?
        """,
        (
            nickname if nickname is not None else member["nickname"],
            furnace_lv if furnace_lv is not None else member["furnace_lv"],
            kid if kid is not None else member["kid"],
            stove_lv_content
            if stove_lv_content is not None
            else member["stove_lv_content"],
            next_alliance,
            fid,
        ),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )


def remove_member(fid: int) -> None:
    database.execute(
        "DELETE FROM users WHERE fid = ?",
        (fid,),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )


def get_member(fid: int) -> Optional[Dict]:
    alliances = _alliances_lookup()
    member = database.fetch_one(
        "SELECT fid, nickname, furnace_lv, kid, stove_lv_content, alliance FROM users WHERE fid = ?",
        (fid,),
        db_path=database.USERS_DB_PATH,
        ensure=database.ensure_users_schema,
    )
    if member is None:
        return None

    alliance_value = member.get("alliance")
    alliance_int = _to_int(alliance_value)
    member["alliance_id"] = alliance_int
    member["alliance_name"] = (
        alliances.get(alliance_int) if alliance_int is not None else None
    )
    return member


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
    "get_member",
]
