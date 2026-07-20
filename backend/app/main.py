from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="GateMind AI",
    description="Personal GATE DA 2027 preparation platform — API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

app.include_router(api_router)


@app.get("/api/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": "GateMind AI", "env": settings.APP_ENV}


# ---- Serve the built frontend (single-service deploy) ----
# In production (Docker) the Vite build is copied to backend/static; then FastAPI serves the SPA
# from the same origin as the API (no CORS). Locally there is no static/ dir, so dev keeps using
# the Vite server on :5173 and this block is a no-op.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir() and (STATIC_DIR / "index.html").is_file():
    _index = STATIC_DIR / "index.html"
    if (STATIC_DIR / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        # API/uploads paths that reach here are genuinely unknown — return JSON 404, not the SPA.
        if full_path.startswith(("api/", "uploads/")):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_index))  # client-side route → SPA entry
