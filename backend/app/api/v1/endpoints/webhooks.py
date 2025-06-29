import os
import json
from fastapi import APIRouter, Request, HTTPException, Response
from typing import Optional

from app.services.facebook_service import FacebookService

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
async def handle_facebook_webhook(request: Request):
    """
    Handles incoming events from the Facebook webhook, such as new comments.
    """
    data = await request.json()
    print("Received Facebook Webhook Event:")
    print(json.dumps(data, indent=2))

    # TODO: Add logic to parse the event and trigger the Genie Matching Engine
    
    return {"status": "success"} 