"""Centralised logging helpers for the backend."""

from __future__ import annotations

from typing import Dict, List

from . import database


def record_log(category: str, message: str) -> int:
    return database.execute(
        "INSERT INTO logs (category, message) VALUES (?, ?)",
        (category, message),
    )


def list_logs(limit: int = 200) -> List[Dict]:
    return database.fetch_all(
        "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )


__all__ = ["record_log", "list_logs"]
