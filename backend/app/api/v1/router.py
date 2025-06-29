from fastapi import APIRouter
from app.api.v1.endpoints import leads, dashboard, opportunities, webhooks

api_router = APIRouter()
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
