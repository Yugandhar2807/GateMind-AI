from fastapi import APIRouter

from app.api.v1.routers import (
    admin,
    auth,
    bookmarks,
    dashboard,
    flashcards,
    notes,
    practice,
    roadmap,
    study,
    users,
)

# Feature routers, rebuilt on the greenfield UUID/Postgres schema phase-by-phase.
# P5: auth + users. P7: roadmap. P6: dashboard + study. P8: notes + flashcards + bookmarks.
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roadmap.router)
api_router.include_router(dashboard.router)
api_router.include_router(study.router)
api_router.include_router(notes.router)
api_router.include_router(flashcards.router)
api_router.include_router(bookmarks.router)
api_router.include_router(practice.router)
api_router.include_router(admin.router)
