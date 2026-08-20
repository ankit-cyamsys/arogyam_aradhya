from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import auth, members, catalog, orders, mlm, admin, public

app = FastAPI(title="Arogyam Aradhya API", version="1.0.0")

# ---- CORS ----
_origins = settings.cors_origins_list
if "*" in _origins:
    # Wildcard can't be combined with credentials per the CORS spec.
    # We authenticate with Bearer tokens (headers), not cookies, so this is fine.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---- Product / media static files ----
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ---- API routers ----
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(catalog.router)
app.include_router(orders.router)
app.include_router(mlm.router)
app.include_router(admin.router)
app.include_router(public.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "company": settings.COMPANY_NAME}


# ---- Serve the built React SPA (single-service deploy) ----
def _find_frontend_dist() -> Path | None:
    env = os.getenv("FRONTEND_DIST")
    candidates = [Path(env)] if env else []
    here = Path(__file__).resolve()
    candidates += [
        here.parents[2] / "frontend" / "dist",  # repo layout: backend/app/main.py
        Path("/app/frontend/dist"),               # docker layout
        here.parents[1] / "frontend_dist",        # bundled next to backend
    ]
    for c in candidates:
        if c and (c / "index.html").is_file():
            return c
    return None


FRONTEND_DIST = _find_frontend_dist()
if FRONTEND_DIST:
    # Serve hashed assets and any real file; fall back to index.html for SPA routes.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        if full_path.startswith(("api", "static", "docs", "openapi.json", "redoc")):
            return FileResponse(FRONTEND_DIST / "index.html", status_code=404)
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
