"""FastAPI application exposing the former Discord bot functionality as REST APIs."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from ..shared import auth, database
from .routes import register_routers


def create_app() -> FastAPI:
    database.ensure_database()
    auth.ensure_admin_user()

    app = FastAPI(title="Whiteout Survival Control Center")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_url, "http://localhost:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    session_secret = os.getenv("SESSION_SECRET", "super-secret-key")
    app.add_middleware(SessionMiddleware, secret_key=session_secret)

    register_routers(app)

    @app.get("/health")
    def healthcheck():
        return {"status": "ok"}

    return app


app = create_app()


__all__ = ["app", "create_app"]
