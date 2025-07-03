from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
from datetime import datetime

# Add project root to the Python path if running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.services.sam_service import SamService
from app.db.client import get_db
from app.db.models import Opportunity, Lead

router = APIRouter()

@router.post("/run-opportunity-pipeline", status_code=201, summary="Trigger the full opportunity sourcing and lead creation pipeline.")
def run_opportunity_pipeline(db: Session = Depends(get_db)):
    """
    This endpoint triggers the full pipeline:
    1. Fetches opportunities from SAM.gov based on a predefined set of keywords.
    2. Stores any new opportunities in the database.
    3. Creates initial 'Identified' placeholder leads for each new opportunity.
    """
    sam_service = SamService()
    # For now, we'll use a static list of keywords. This could be moved to config later.
    keywords = ["IT", "Construction", "Software", "Consulting"]
    
    opportunities_data = sam_service.fetch_opportunities(keywords)
    
    new_opportunities_count = 0
    new_leads_count = 0

    for opp_data in opportunities_data:
        # Check if opportunity already exists to prevent duplicates
        exists = db.query(Opportunity).filter(Opportunity.url == opp_data["url"]).first()
        if exists is None:
            new_opp = Opportunity(
                title=opp_data["title"],
                agency=opp_data["agency"],
                posted_date=datetime.fromisoformat(opp_data["posted_date"]),
                url=opp_data["url"]
            )
            db.add(new_opp)
            db.commit()
            db.refresh(new_opp)
            new_opportunities_count += 1
            
            # For each new opportunity, create a placeholder lead
            # This lead will be enriched by the prospecting step.
            new_lead = Lead(
                business_name="Placeholder Business", 
                opportunity_id=new_opp.id,
                status="Identified"
            )
            db.add(new_lead)
            db.commit()
            new_leads_count += 1

    return {
        "message": "Opportunity pipeline run complete.",
        "new_opportunities_added": new_opportunities_count,
        "new_leads_created": new_leads_count,
    } 