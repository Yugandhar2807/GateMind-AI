from fastapi import APIRouter

from app.api.v1.routers import auth, users

# Feature routers are rebuilt on the greenfield UUID/Postgres schema phase-by-phase.
# Phase 5: auth + users. (roadmap, dashboard, notes, flashcards, bookmarks, practice → P6+.)
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
