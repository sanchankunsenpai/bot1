"""Authentication utilities for the web application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from passlib.context import CryptContext

from . import database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class User:
    id: int
    username: str
    role: str


def get_user_by_username(username: str) -> Optional[User]:
    row = database.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    if not row:
        return None
    return User(id=row["id"], username=row["username"], role=row["role"])


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def ensure_admin_user(username: str = "admin", password: str = "admin") -> None:
    """Create a default administrator if none exist."""

    row = database.fetch_one("SELECT id FROM users LIMIT 1")
    if row:
        return

    password_hash = get_password_hash(password)
    database.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
        (username, password_hash),
    )


def authenticate(username: str, password: str) -> Optional[User]:
    row = database.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    if not row:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return User(id=row["id"], username=row["username"], role=row["role"])


__all__ = [
    "User",
    "authenticate",
    "ensure_admin_user",
    "get_user_by_username",
    "get_password_hash",
]
