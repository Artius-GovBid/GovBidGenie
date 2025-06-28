from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.client import get_db
from app.db.models import Lead, Opportunity
from pydantic import BaseModel

router = APIRouter()

class OpportunitySchema(BaseModel):
    title: str
    agency: str
    url: Optional[str]

    class Config:
        from_attributes = True

class LeadSchema(BaseModel):
    id: int
    status: str
    azure_devops_work_item_id: Optional[int]
    opportunity: OpportunitySchema

    class Config:
        from_attributes = True

@router.get("/leads", response_model=List[LeadSchema])
def get_all_leads(db: Session = Depends(get_db)):
    """
    Retrieve all leads with their associated opportunity data.
    """
    leads = db.query(Lead).join(Opportunity).all()
    return leads
