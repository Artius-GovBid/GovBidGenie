import os
import json
from fastapi import APIRouter, Request, HTTPException, Response
from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.facebook_service import FacebookService
from app.services.lead_service import LeadService
from app.db.client import get_db

router = APIRouter()

VERIFY_TOKEN = os.environ.get("FACEBOOK_VERIFY_TOKEN")
if not VERIFY_TOKEN:
    raise ValueError("FACEBOOK_VERIFY_TOKEN environment variable must be set.")

@router.get("/facebook", summary="Facebook Webhook Verification")
async def verify_facebook_webhook(request: Request):
    """
    Handles Facebook's webhook verification challenge.
    """
    print("--- Received GET request on /facebook webhook. ---")
    params = request.query_params
    hub_mode = params.get('hub.mode')
    hub_challenge = params.get('hub.challenge')
    hub_verify_token = params.get('hub.verify_token')
    
    print(f"Mode: {hub_mode}, Token: {hub_verify_token}, Challenge: {hub_challenge}")
    print(f"Expected Token: {VERIFY_TOKEN}")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Facebook Webhook Verified.")
        return Response(content=str(hub_challenge), media_type="text/plain")
    else:
        print("❌ Verification Failed.")
        raise HTTPException(status_code=403, detail="Verify token does not match.")


@router.post("/facebook", summary="Handle Facebook Webhook Events")
async def handle_facebook_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming events from the Facebook webhook, such as new comments.
    """
    data = await request.json()
    print("--- Received Facebook POST Event ---")
    print(json.dumps(data, indent=2))

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            # Find the 'changes' field for feed events, or 'messaging' for message events
            changes = entry.get("changes", [])
            
            for change in changes:
                if change.get("field") == "feed" and change.get("value", {}).get("item") == "comment":
                    try:
                        comment_data = change["value"]
                        # Ensure we are getting a new comment, not an edit
                        if comment_data.get('verb') != 'add':
                            continue

                        commenter_id = comment_data.get("from", {}).get("id")
                        comment_text = comment_data.get("message")
                        
                        if not commenter_id or not comment_text:
                            print("Skipping event with missing data.")
                            continue

                        print(f"Processing new comment from user {commenter_id}")
                        lead_service = LeadService(db)
                        lead_service.find_and_create_lead_from_comment(commenter_id, comment_text)

                    except Exception as e:
                        print(f"ERROR: Failed to process comment. Error: {e}")
                        pass
    
    return {"status": "success"} 