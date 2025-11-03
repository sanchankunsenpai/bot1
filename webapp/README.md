# Whiteout Survival Control Center

This directory contains the web application rewrite of the original Whiteout Survival Discord bot. The web stack keeps all core features (alliances, attendance, ministers, gift codes, events, and audit logs) while exposing them through a modern React + FastAPI dashboard.

## Project structure

```
webapp/
  backend/           # FastAPI application with REST endpoints
  frontend/          # React + Tailwind dashboard
  shared/            # Reusable logic migrated from the Discord bot
```

## Backend

### Prerequisites

* Python 3.11+
* The ONNX runtime dependencies listed in `requirements.txt`
* The existing `models/` directory containing `captcha_model.onnx`

### Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn webapp.backend.app:app --reload
```

The API listens on `http://127.0.0.1:8000`. Swagger documentation is available at `/docs` after authentication.

### Environment variables

* `FRONTEND_URL` – optional override for CORS (default `http://localhost:5173`).
* `SESSION_SECRET` – secret key for session cookies.

## Frontend

The frontend is a Vite + React + Tailwind project. Install dependencies and run the dev server:

```bash
cd webapp/frontend
npm install
npm run dev
```

The development server runs on `http://localhost:5173` and proxies API calls to the FastAPI backend (configure in `src/api/client.js`).

## Docker

A multi-stage Dockerfile is provided to build both the backend and frontend bundles.

```bash
docker build -t whiteout-control-center -f webapp/Dockerfile .
docker run -p 8000:8000 whiteout-control-center
```

The container serves the FastAPI app with static assets built from the frontend.

## Deployment

The application can be deployed to Render, Railway, or any container platform by pointing to `webapp/Dockerfile`. For serverless frontend hosting (e.g. Vercel), build the frontend with `npm run build` and host the generated `dist/` directory while deploying the FastAPI backend separately.

## Mapping from the Discord bot

* Alliance, member, and minister operations mirror the SQL logic from the original cogs but are exposed as REST endpoints.
* Gift code redemption reuses the ONNX captcha solver (`shared/gift_captcha_solver.py`).
* Attendance and event tracking retain their underlying tables while providing chart-ready summaries.
* Audit logs replace Discord embeds and DM confirmations with persistent history accessible from the Settings/Logs dashboard.

## Default login

On first launch the backend seeds an administrator account:

* **Username:** `admin`
* **Password:** `admin`

Change the password immediately via the Settings view.
