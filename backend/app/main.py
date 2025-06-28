import os
from fastapi import FastAPI, HTTPException, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any

from app.db.models import Base, Opportunity, Lead
from app.services.sam_service import SAMService
from app.services.devops_service import DevOpsService
from app.services.facebook_service import FacebookService

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

app = FastAPI()

# --- Services ---
sam_service = SAMService()
devops_service = DevOpsService()
facebook_service = FacebookService()


@app.on_event("startup")
async def startup_event():
    # This is where you might initialize other services or connections
    pass


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


@app.post("/api/v1/leads", status_code=201)
def create_lead_from_opportunity(opportunity_data: Dict[str, Any]):
    db = SessionLocal()
    try:
        sam_gov_id = opportunity_data.get("sam_gov_id")
        if not sam_gov_id:
            raise HTTPException(status_code=400, detail="sam_gov_id is required")

        # 1. Find or create the Opportunity
        opportunity = db.query(Opportunity).filter(Opportunity.sam_gov_id == sam_gov_id).first()
        if not opportunity:
            opportunity = Opportunity(
                sam_gov_id=sam_gov_id,
                title=opportunity_data.get("title", "N/A"),
                url=opportunity_data.get("url"),
                agency=opportunity_data.get("agency"),
                posted_date=opportunity_data.get("posted_date")
            )
            db.add(opportunity)
            db.commit()
            db.refresh(opportunity)

        # 2. Create the Lead
        new_lead = Lead(
            opportunity_id=opportunity.id,
            source="SAM.gov",
            status="IDENTIFIED"
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)

        # 3. Create the Azure DevOps Work Item
        try:
            work_item_id = devops_service.create_work_item({
                "opportunity_id": opportunity.id,
                "business_name": new_lead.business_name # Will be null initially
            })
            new_lead.azure_devops_work_item_id = work_item_id
            db.commit()
            db.refresh(new_lead)
        except Exception as e:
            # Log the error, but don't fail the entire request
            # In a real app, you'd have a more robust retry/queueing mechanism
            print(f"ERROR: Failed to create ADO work item for lead {new_lead.id}. Error: {e}")


        return {"lead_id": new_lead.id, "opportunity_id": opportunity.id, "azure_devops_work_item_id": new_lead.azure_devops_work_item_id}

    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "GovBidGenie Backend is running"}
