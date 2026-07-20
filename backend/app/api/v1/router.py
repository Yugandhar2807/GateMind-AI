from fastapi import APIRouter

from app.api.v1.routers import auth, bookmarks, dashboard, flashcards, notes, practice, roadmap, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roadmap.router)
api_router.include_router(dashboard.router)
api_router.include_router(notes.router)
api_router.include_router(flashcards.router)
api_router.include_router(bookmarks.router)
api_router.include_router(practice.router)
