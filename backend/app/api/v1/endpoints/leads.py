from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.client import get_db
from app.services.lead_service import LeadService
from app.services.devops_service import DevOpsService
from pydantic import BaseModel, HttpUrl
from datetime import datetime

router = APIRouter()

class LeadCreateSchema(BaseModel):
    sam_gov_id: str
    title: str
    url: HttpUrl
    agency: str
    posted_date: datetime

@router.post("/", status_code=201)
def create_lead(lead_in: LeadCreateSchema, db: Session = Depends(get_db)):
    """
    Create a new lead from a SAM.gov opportunity.
    """
    lead_service = LeadService(db)
    devops_service = DevOpsService()

    # Check if a lead for this opportunity already exists
    existing_lead = lead_service.get_lead_by_sam_id(lead_in.sam_gov_id)
    if existing_lead:
        raise HTTPException(
            status_code=409, 
            detail=f"A lead for SAM.gov ID '{lead_in.sam_gov_id}' already exists."
        )

    # 1. Create the lead in the local database
    new_lead = lead_service.create_lead(
        sam_gov_id=lead_in.sam_gov_id,
        title=lead_in.title,
        url=str(lead_in.url),
        agency=lead_in.agency,
        posted_date=lead_in.posted_date
    )

    # 2. Create a work item in Azure DevOps
    # We need to get the opportunity to get the title, url, and agency
    opportunity = new_lead.opportunity
    work_item = devops_service.create_work_item(
        title=f"New Lead: {opportunity.title}",
        opportunity_url=opportunity.url,
        agency=opportunity.agency,
        source="SAM.gov"
    )
    
    # 3. Update the lead with the DevOps work item ID
    ado_id = work_item['id']
    lead_service.update_lead_ado_id(new_lead.id, ado_id)

    return {
        "message": "Lead and Azure DevOps work item created successfully.",
        "lead_id": new_lead.id,
        "azure_devops_work_item_id": ado_id,
    }
