"""Gift code management helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


def _to_int(value) -> Optional[int]:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def list_gift_codes(alliance_id: Optional[int] = None) -> List[Dict]:
    if alliance_id is None:
        rows = database.fetch_all(
            "SELECT giftcode, date, alliance_id, validation_status, created_at FROM gift_codes ORDER BY created_at DESC",
            db_path=database.GIFTCODE_DB_PATH,
            ensure=database.ensure_giftcode_schema,
        )
    else:
        rows = database.fetch_all(
            """
            SELECT giftcode, date, alliance_id, validation_status, created_at
            FROM gift_codes
            WHERE alliance_id = ? OR alliance_id = ?
            ORDER BY created_at DESC
            """,
            (alliance_id, str(alliance_id)),
            db_path=database.GIFTCODE_DB_PATH,
            ensure=database.ensure_giftcode_schema,
        )

    for row in rows:
        row["alliance_id"] = _to_int(row.get("alliance_id"))
    return rows


def upsert_gift_code(
    code: str,
    *,
    alliance_id: Optional[int] = None,
    validation_status: str = "pending",
) -> None:
    existing = database.fetch_one(
        "SELECT giftcode FROM gift_codes WHERE giftcode = ?",
        (code,),
        db_path=database.GIFTCODE_DB_PATH,
        ensure=database.ensure_giftcode_schema,
    )
    if existing:
        database.execute(
            """
            UPDATE gift_codes
            SET alliance_id = ?, validation_status = ?, date = CURRENT_TIMESTAMP
            WHERE giftcode = ?
            """,
            (alliance_id if alliance_id is not None else None, validation_status, code),
            db_path=database.GIFTCODE_DB_PATH,
            ensure=database.ensure_giftcode_schema,
        )
    else:
        database.execute(
            """
            INSERT INTO gift_codes (giftcode, date, alliance_id, validation_status)
            VALUES (?, CURRENT_TIMESTAMP, ?, ?)
            """,
            (code, alliance_id if alliance_id is not None else None, validation_status),
            db_path=database.GIFTCODE_DB_PATH,
            ensure=database.ensure_giftcode_schema,
        )


def update_gift_code_status(code: str, validation_status: str) -> None:
    database.execute(
        "UPDATE gift_codes SET validation_status = ?, date = CURRENT_TIMESTAMP WHERE giftcode = ?",
        (validation_status, code),
        db_path=database.GIFTCODE_DB_PATH,
        ensure=database.ensure_giftcode_schema,
    )


def delete_gift_code(code: str) -> None:
    database.execute(
        "DELETE FROM gift_codes WHERE giftcode = ?",
        (code,),
        db_path=database.GIFTCODE_DB_PATH,
        ensure=database.ensure_giftcode_schema,
    )


__all__ = [
    "list_gift_codes",
    "upsert_gift_code",
    "update_gift_code_status",
    "delete_gift_code",
]
