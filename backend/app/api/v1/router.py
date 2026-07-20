from fastapi import APIRouter

# Feature routers (auth, users, roadmap, dashboard, notes, flashcards, bookmarks, practice)
# are being rebuilt on the greenfield UUID/Postgres schema phase-by-phase (Phase 5+).
# Until then the API exposes only /api/health (defined in app.main).
api_router = APIRouter(prefix="/api/v1")
