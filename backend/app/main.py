import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any
from starlette.middleware.cors import CORSMiddleware

from app.db.models import Base, Opportunity, Lead
from app.services.sam_service import SAMService
from app.services.devops_service import DevOpsService
from app.services.facebook_service import FacebookService
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.client import db_client
from app.jobs.scheduler import scheduler

# Load environment variables from .env file
load_dotenv()

# --- Environment Variables ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

FACEBOOK_VERIFY_TOKEN = os.environ.get("FACEBOOK_VERIFY_TOKEN")
if not FACEBOOK_VERIFY_TOKEN:
    raise ValueError("FACEBOOK_VERIFY_TOKEN environment variable is not set.")


# --- Database Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
# ... (rest of CORS middleware configuration)

# --- Services ---
sam_service = SAMService()
devops_service = DevOpsService()
facebook_service = FacebookService()


@app.on_event("startup")
def startup_event():
    db_client.connect()
    # No need to check for Supabase, direct DB connection now
    print("--- Database connection established. ---")
    
    # Start the background scheduler
    if not scheduler.running:
        scheduler.start()
        print("--- Background scheduler started. ---")


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        print("--- Background scheduler shut down. ---")
    
    db_client.disconnect()


@app.get("/")
def read_root():
    return {"message": "GovBidGenie Backend is running"}

app.include_router(api_router, prefix=settings.API_V1_STR)
