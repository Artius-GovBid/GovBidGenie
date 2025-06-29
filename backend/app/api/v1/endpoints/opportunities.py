from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.client import get_db
from app.db.models import Opportunity, Lead
from pydantic import BaseModel

router = APIRouter()

class OpportunitySchema(BaseModel):
    id: int
    title: str
    agency: str
    url: Optional[str]
    posted_date: datetime
    source: Optional[str]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[OpportunitySchema])
def get_available_opportunities(db: Session = Depends(get_db)):
    """
    Retrieve all opportunities that have not yet been converted into a lead.
    """
    available_opportunities = (
        db.query(Opportunity)
        .outerjoin(Lead, Opportunity.id == Lead.opportunity_id)
        .filter(Lead.id == None)
        .order_by(Opportunity.posted_date.desc())
        .all()
    )
    return available_opportunities 