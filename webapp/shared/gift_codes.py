"""Gift code management helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from . import database


def list_gift_codes(alliance_id: Optional[int] = None) -> List[Dict]:
    if alliance_id is None:
        return database.fetch_all("SELECT * FROM gift_codes ORDER BY created_at DESC")
    return database.fetch_all(
        "SELECT * FROM gift_codes WHERE alliance_id = ? ORDER BY created_at DESC",
        (alliance_id,),
    )


def upsert_gift_code(code: str, *, alliance_id: Optional[int] = None, status: str = "pending", redeemed_by: Optional[str] = None, validation_status: str = "pending", confidence: Optional[float] = None) -> int:
    existing = database.fetch_one("SELECT id FROM gift_codes WHERE code = ?", (code,))
    if existing:
        database.execute(
            """
            UPDATE gift_codes
            SET alliance_id = ?, status = ?, redeemed_by = ?, validation_status = ?, confidence = ?, last_checked_at = CURRENT_TIMESTAMP
            WHERE code = ?
            """,
            (alliance_id, status, redeemed_by, validation_status, confidence, code),
        )
        return existing["id"]
    return database.execute(
        """
        INSERT INTO gift_codes (code, alliance_id, status, redeemed_by, validation_status, confidence, last_checked_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (code, alliance_id, status, redeemed_by, validation_status, confidence),
    )


def update_gift_code_status(code_id: int, status: str, *, redeemed_by: Optional[str] = None) -> None:
    database.execute(
        "UPDATE gift_codes SET status = ?, redeemed_by = ?, redeemed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, redeemed_by, code_id),
    )


def delete_gift_code(code_id: int) -> None:
    database.execute("DELETE FROM gift_codes WHERE id = ?", (code_id,))


__all__ = [
    "list_gift_codes",
    "upsert_gift_code",
    "update_gift_code_status",
    "delete_gift_code",
]
