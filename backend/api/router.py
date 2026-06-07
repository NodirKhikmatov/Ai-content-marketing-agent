from fastapi import APIRouter

from api.v1 import ai, analysis, health, jobs, projects, users, websites

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ai.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(analysis.router)
api_router.include_router(websites.router)
api_router.include_router(jobs.router)
