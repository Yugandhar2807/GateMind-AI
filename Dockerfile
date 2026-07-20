# syntax=docker/dockerfile:1
# GateMind AI — single-service full-stack image (frontend built by Node, served by FastAPI).

# ---- Stage 1: build the React/Vite frontend ----
FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: FastAPI backend that also serves the built SPA ----
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/ ./
# The built SPA is served by app/main.py from ./static (same origin as the API).
COPY --from=frontend /app/frontend/dist ./static

EXPOSE 8000
# Apply DB migrations, then start. $PORT is injected by Render (falls back to 8000 locally).
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
