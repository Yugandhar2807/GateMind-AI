from fastapi import APIRouter

from app.api.v1.routers import auth, dashboard, roadmap, study, users

# Feature routers, rebuilt on the greenfield UUID/Postgres schema phase-by-phase.
# P5: auth + users. P7: roadmap. P6: dashboard + study sessions.
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roadmap.router)
api_router.include_router(dashboard.router)
api_router.include_router(study.router)
