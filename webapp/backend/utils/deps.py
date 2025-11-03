"""FastAPI dependency utilities."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from ...shared import auth


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    username = request.session.get("username")
    role = request.session.get("role", "admin")
    return auth.User(id=user_id, username=username, role=role)


__all__ = ["get_current_user"]
