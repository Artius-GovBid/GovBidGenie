import os
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


@app.post("/webhook/facebook")
async def facebook_webhook_post(request: Request):
    """
    Handles incoming webhook events from Facebook.
    Specifically processes new comments on page posts.
    """
    data = await request.json()
    print(f"Received Facebook webhook data: {data}")

    # Ensure the event is for a page and contains feed changes
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "feed" and change.get("value", {}).get("item") == "comment":
                    try:
                        comment_data = change["value"]
                        comment_id = comment_data["comment_id"]
                        
                        # Here, you would add logic to verify this is a comment you want to reply to.
                        # For now, we will reply to any comment as a demonstration.
                        
                        print(f"Processing new comment with ID: {comment_id}")
                        reply_message = "Thank you for your comment! We've sent you a private message to follow up."

                        facebook_service.send_private_reply(
                            comment_id=comment_id,
                            message=reply_message
                        )
                        print(f"Successfully sent private reply to comment {comment_id}")

                    except Exception as e:
                        print(f"ERROR: Failed to process comment or send reply. Error: {e}")
                        # Return 200 to Facebook anyway, so it doesn't retry a failed event.
                        pass

    return Response(status_code=200)

@app.get("/webhook/facebook")
async def facebook_webhook_get(request: Request):
    """
    Handles Facebook's webhook verification request.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == FACEBOOK_VERIFY_TOKEN:
        print("Facebook webhook verification successful!")
        return Response(content=challenge, status_code=200)
    else:
        print("Facebook webhook verification failed.")
        raise HTTPException(status_code=403, detail="Verification token mismatch.")


@app.get("/")
def read_root():
    return {"message": "GovBidGenie Backend is running"}

app.include_router(api_router, prefix=settings.API_V1_STR)
