"""API router registration."""

from __future__ import annotations

from fastapi import FastAPI

from . import alliances, auth, events, gift_codes, logs, members, ministers

ROUTERS = [
    auth.router,
    alliances.router,
    members.router,
    gift_codes.router,
    events.router,
    ministers.router,
    logs.router,
]


def register_routers(app: FastAPI) -> None:
    for router in ROUTERS:
        app.include_router(router)


__all__ = ["register_routers"]
