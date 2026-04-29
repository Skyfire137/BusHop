from fastapi import APIRouter
from app.api.v1.endpoints import routes, schedules, scrape_jobs

api_router = APIRouter()
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(scrape_jobs.router, prefix="/scrape-jobs", tags=["scrape-jobs"])
