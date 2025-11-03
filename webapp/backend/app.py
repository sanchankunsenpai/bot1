"""FastAPI application exposing the former Discord bot functionality as REST APIs."""

from __future__ import annotations

import os

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from ..shared import auth, database
from .routes import register_routers


def create_app() -> FastAPI:
    database.ensure_database()
    auth.ensure_admin_user()

    app = FastAPI(title="Whiteout Survival Control Center")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    candidate_origins = [frontend_url, "http://localhost:3000"]
    allowed_origins = [origin for origin in candidate_origins if origin != "*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    session_secret = os.getenv("SESSION_SECRET", "super-secret-key")
    app.add_middleware(SessionMiddleware, secret_key=session_secret)

    register_routers(app)

    # Serve the compiled frontend if it is available (e.g. inside the Docker image)
    dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    index_file = dist_dir / "index.html"
    if index_file.exists():
        assets_dir = dist_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/", include_in_schema=False)
        def serve_spa_root():  # pragma: no cover - thin wrapper around static asset
            return FileResponse(index_file)

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str):  # pragma: no cover - thin wrapper around static asset
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404)
            candidate = (dist_dir / full_path).resolve()
            try:
                candidate.relative_to(dist_dir)
            except ValueError as exc:  # path traversal guard
                raise HTTPException(status_code=404) from exc
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(index_file)

    @app.get("/health")
    def healthcheck():
        return {"status": "ok"}

    return app


app = create_app()


__all__ = ["app", "create_app"]
