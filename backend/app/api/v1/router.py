from fastapi import APIRouter

from app.api.v1.routers import auth, roadmap, users

# Feature routers are rebuilt on the greenfield UUID/Postgres schema phase-by-phase.
# Phase 5: auth + users. Phase 7: roadmap. (dashboard, notes, flashcards, bookmarks, practice → next.)
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roadmap.router)
