from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.models import Lead
from app.db.client import SessionLocal, get_db
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

def create_devops_work_item_task(lead_id: int):
    """
    Background task to create a DevOps work item and update the lead.
    It creates its own database session.
    """
    db = SessionLocal()
    try:
        lead_service = LeadService(db)
        devops_service = DevOpsService()

        lead = db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if not lead or not lead.opportunity:
            print(f"BACKGROUND_TASK_ERROR: Could not find lead or opportunity for lead_id: {lead_id}")
            return

        opportunity = lead.opportunity
        
        work_item = devops_service.create_work_item(
            title=f"New Lead: {opportunity.title}",
            opportunity_url=opportunity.url,
            agency=opportunity.agency,
            source="SAM.gov"
        )
        
        ado_id = work_item['id']
        lead_service.update_lead_ado_id(lead.id, ado_id)
        print(f"BACKGROUND_TASK_SUCCESS: Created ADO work item {ado_id} for lead {lead.id}")
    
    except Exception as e:
        print(f"BACKGROUND_TASK_ERROR: Failed for lead {lead.id}: {e}")
    finally:
        db.close()

@router.post("/", status_code=202)
def create_lead(
    lead_in: LeadCreateSchema, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new lead from a SAM.gov opportunity and schedule a background
    task to create the corresponding Azure DevOps work item.
    """
    lead_service = LeadService(db)

    existing_lead = lead_service.get_lead_by_sam_id(lead_in.sam_gov_id)
    if existing_lead:
        raise HTTPException(
            status_code=409, 
            detail=f"A lead for SAM.gov ID '{lead_in.sam_gov_id}' already exists."
        )

    new_lead = lead_service.create_lead(
        sam_gov_id=lead_in.sam_gov_id,
        title=lead_in.title,
        url=str(lead_in.url),
        agency=lead_in.agency,
        posted_date=lead_in.posted_date
    )

    background_tasks.add_task(create_devops_work_item_task, new_lead.id)

    return {
        "message": "Lead creation accepted. Azure DevOps work item will be created in the background.",
        "lead_id": new_lead.id,
    }
