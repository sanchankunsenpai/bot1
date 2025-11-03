"""API router registration."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI

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
    api_router = APIRouter(prefix="/api")
    for router in ROUTERS:
        api_router.include_router(router)
    app.include_router(api_router)


__all__ = ["register_routers"]
