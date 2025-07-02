from fastapi import FastAPI
from dotenv import load_dotenv
import logging
import os
from typing import Optional

# Load environment variables from .env file FIRST
load_dotenv()

from app.api.v1.router import api_router
from app.jobs.scheduler import SchedulerService
from app.db.client import SessionLocal
from sqlalchemy.orm import Session
from app.services.sam_service import SAMService
from app.services.facebook_service import FacebookService
from app.services.naics_service import NAICSService
from app.services.psc_service import PSCService
from app.services.lead_service import LeadService
from app.services.conversation_service import ConversationService
from app.services.devops_service import DevOpsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App ---
app = FastAPI(
    title="GovBidGenie API",
    description="API for GovBidGenie, a service to generate leads from government contract opportunities.",
    version="1.0.0"
)

# --- Global variables for services ---
scheduler_service: Optional[SchedulerService] = None


@app.on_event("startup")
async def startup_event():
    global scheduler_service

    logger.info("--- Starting up application ---")

    db_session_factory = SessionLocal
    
    # --- Service Initialization ---
    facebook_page_id = os.environ.get("FACEBOOK_PAGE_ID")
    facebook_access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")

    facebook_service = FacebookService(
        page_id=facebook_page_id, 
        access_token=facebook_access_token
    )
    
    sam_service = SAMService()
    naics_service = NAICSService()
    psc_service = PSCService()
    devops_service = DevOpsService()
    
    lead_service = LeadService(
        db_session_factory=db_session_factory,
        facebook_service=facebook_service,
        naics_service=naics_service
    )
    
    conversation_service = ConversationService(
        db_session_factory=db_session_factory,
        facebook_service=facebook_service
    )

    # Initialize and start scheduler
    scheduler_service = SchedulerService(
        sam_service=sam_service,
        lead_service=lead_service,
        conversation_service=conversation_service,
        devops_service=devops_service,
        db_session_factory=db_session_factory
    )
    
    scheduler = scheduler_service.get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("--- Background scheduler started. ---")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("--- Shutting down application ---")
    if scheduler_service:
        scheduler = scheduler_service.get_scheduler()
        if scheduler and scheduler.running:
            scheduler.shutdown()
            logger.info("--- Background scheduler stopped. ---")
    logger.info("--- Application shutdown complete. ---")

# --- API Router ---
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to GovBidGenie"}