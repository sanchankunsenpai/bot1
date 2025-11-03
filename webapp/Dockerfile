# syntax=docker/dockerfile:1.7

# ----------------------
# Frontend build stage
# ----------------------
FROM node:20-alpine AS frontend
WORKDIR /app
COPY webapp/frontend/package*.json ./
RUN npm install
COPY webapp/frontend ./
RUN npm run build

# ----------------------
# Backend stage
# ----------------------
FROM python:3.11-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Copy frontend build artefacts into the backend for static serving
COPY --from=frontend /app/dist webapp/frontend/dist

EXPOSE 8000

CMD ["uvicorn", "webapp.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
