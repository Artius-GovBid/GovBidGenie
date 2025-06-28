from fastapi import APIRouter
from app.api.v1.endpoints import leads, dashboard

api_router = APIRouter()
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
