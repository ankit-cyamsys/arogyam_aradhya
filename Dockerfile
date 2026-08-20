# ---------- Stage 1: build the React frontend ----------
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: Python backend that also serves the built SPA ----------
FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FRONTEND_DIST=/app/frontend/dist

WORKDIR /app/backend

# Install backend dependencies first (better layer caching)
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

# Backend source (includes bundled product images under app/static/products)
COPY backend/ ./

# Built frontend from stage 1
COPY --from=frontend /frontend/dist /app/frontend/dist

EXPOSE 8000

# Create tables + seed on first boot (idempotent), then start the server.
# Render provides $PORT; default to 8000 locally.
CMD ["sh", "-c", "python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
