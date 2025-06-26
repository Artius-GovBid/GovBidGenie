from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
from pydantic import BaseModel

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sam_service import SamService
from app.db.client import get_db, SessionLocal
from app.db.models import Opportunity, Lead, ConversationLog, Appointment
from datetime import datetime
from app.services.facebook_service import FacebookService
from app.services.conversation_service import ConversationService
from app.services.calendar_service import CalendarService

app = FastAPI(title="Government Lead Genie", version="0.1.0")

class IncomingMessage(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Government Lead Genie API"}

@app.post("/run-opportunity-pipeline", status_code=201)
def run_opportunity_pipeline(db: Session = Depends(get_db)):
    """
    This endpoint triggers the full pipeline:
    1. Fetches opportunities from SAM.gov.
    2. Stores new opportunities in the database.
    3. Creates initial 'Identified' leads for each opportunity.
    """
    sam_service = SamService()
    # For now, we'll use a static list of keywords.
    keywords = ["IT", "Construction"]
    
    opportunities_data = sam_service.fetch_opportunities(keywords)
    
    new_opportunities_count = 0
    new_leads_count = 0

    for opp_data in opportunities_data:
        # Check if opportunity already exists
        exists = db.query(Opportunity).filter(Opportunity.url == opp_data["url"]).first()
        if not exists:
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
            # In the future, this would be replaced by a real prospecting step.
            new_lead = Lead(
                business_name="Placeholder Business", # To be found by Facebook service
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

@app.post("/prospect-lead/{lead_id}", status_code=200)
def prospect_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    This endpoint takes an 'Identified' lead and attempts to find a 
    matching Facebook page for it, updating its status to 'Prospected'.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead.status != "Identified":
        raise HTTPException(status_code=400, detail=f"Lead status is '{lead.status}', not 'Identified'.")

    # Extract keywords from the opportunity title
    keywords = lead.opportunity.title.split()

    facebook_service = FacebookService()
    pages = facebook_service.search_business_pages(keywords)

    if not pages:
        lead.status = "Prospecting Failed"
        db.commit()
        raise HTTPException(status_code=404, detail="No matching Facebook pages found.")

    # For this example, we'll just take the first result
    found_page = pages[0]
    
    lead.business_name = found_page["name"]
    lead.facebook_page_url = found_page["link"]
    lead.status = "Prospected"
    lead.last_updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lead)

    return {
        "message": "Lead successfully prospected.",
        "lead": {
            "id": lead.id,
            "business_name": lead.business_name,
            "facebook_page_url": lead.facebook_page_url,
            "status": lead.status,
        }
    }

@app.post("/engage-lead/{lead_id}", status_code=200)
def engage_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Takes a 'Prospected' lead and runs the engagement sequence (like, share, comment).
    Updates the lead's status to 'Engaged'.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.status != "Prospected":
        raise HTTPException(status_code=400, detail=f"Lead status is '{lead.status}', not 'Prospected'.")

    if not lead.facebook_page_url:
        raise HTTPException(status_code=400, detail="Lead has no Facebook page URL to engage with.")

    facebook_service = FacebookService()
    success = facebook_service.perform_engagement_sequence(lead.facebook_page_url)

    if not success:
        lead.status = "Engagement Failed"
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to perform engagement sequence. Check logs.")

    lead.status = "Engaged"
    lead.last_updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Successfully engaged with lead {lead.id}."}

@app.post("/initiate-conversation/{lead_id}", status_code=200)
def initiate_conversation(lead_id: int, db: Session = Depends(get_db)):
    """
    Takes an 'Engaged' lead, generates an initial message, sends it,
    logs it, and updates the lead's status to 'Messaged'.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.status != "Engaged":
        raise HTTPException(status_code=400, detail=f"Lead status is '{lead.status}', not 'Engaged'.")

    # 1. Generate the initial message
    convo_service = ConversationService()
    message_text = convo_service.generate_initial_message(lead)

    # 2. "Send" the message via FacebookService
    facebook_service = FacebookService()
    # In a real app, the recipient_id would be the Page-Scoped ID (PSID), not the URL.
    # For this mock, we'll use the business name as a stand-in for the ID.
    recipient_id = lead.business_name 
    success = facebook_service.send_direct_message(recipient_id, message_text)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send direct message.")

    # 3. Log the sent message
    new_log = ConversationLog(
        lead_id=lead.id,
        sender="AI",
        message=message_text
    )
    db.add(new_log)
    
    # 4. Update lead status
    lead.status = "Messaged"
    lead.last_updated_at = datetime.utcnow()
    
    db.commit()

    return {"message": f"Successfully initiated conversation with lead {lead.id}."}

@app.post("/conversation-webhook/{lead_id}", status_code=200)
def handle_conversation_message(lead_id: int, incoming_message: IncomingMessage, db: Session = Depends(get_db)):
    """
    Simulates receiving a message from a user, generating and sending a response,
    and logging the entire exchange.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # 1. Log the incoming message from the business
    user_log = ConversationLog(
        lead_id=lead.id,
        sender="Business",
        message=incoming_message.message
    )
    db.add(user_log)
    db.commit()
    db.refresh(user_log)

    # 2. Generate a response
    convo_service = ConversationService()
    conversation_history = db.query(ConversationLog).filter(ConversationLog.lead_id == lead.id).order_by(ConversationLog.timestamp).all()
    ai_response_text = convo_service.generate_response(conversation_history)

    # 3. "Send" the AI's response
    facebook_service = FacebookService()
    recipient_id = lead.business_name # Using name as placeholder ID
    facebook_service.send_direct_message(recipient_id, ai_response_text)
    
    # 4. Log the AI's outgoing message
    ai_log = ConversationLog(
        lead_id=lead.id,
        sender="AI",
        message=ai_response_text
    )
    db.add(ai_log)
    db.commit()

    return {"message": "Response sent and conversation logged."}

class AppointmentRequest(BaseModel):
    start_time: str # ISO 8601 format
    end_time: str   # ISO 8601 format

@app.post("/offer-appointment/{lead_id}", status_code=200)
def offer_appointment(lead_id: int, db: Session = Depends(get_db)):
    """
    Gets available appointment slots and updates lead status to 'Appointment Offered'.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    calendar_service = CalendarService()
    available_slots = calendar_service.get_availability()

    lead.status = "Appointment Offered"
    lead.last_updated_at = datetime.utcnow()
    db.commit()

    # In a real app, the AI would present these slots to the user.
    # For now, we return them from the API.
    return {
        "message": "Appointment slots available. AI should now offer these to the lead.",
        "available_slots": available_slots
    }

@app.post("/book-appointment/{lead_id}", status_code=201)
def book_appointment(lead_id: int, appt_request: AppointmentRequest, db: Session = Depends(get_db)):
    """
    Books an appointment for the lead at a specified time.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    calendar_service = CalendarService()
    # In a real app, you'd need the lead's email. Using a placeholder for now.
    lead_email = f"{lead.business_name.replace(' ', '').lower()}@example.com"
    title = f"Intro Call: GovBidGenie & {lead.business_name}"

    created_event = calendar_service.create_appointment(
        start_time=appt_request.start_time,
        end_time=appt_request.end_time,
        title=title,
        lead_email=lead_email
    )

    # Log the appointment in our database
    new_appointment = Appointment(
        lead_id=lead.id,
        start_time=datetime.fromisoformat(appt_request.start_time.replace("Z", "+00:00")),
        end_time=datetime.fromisoformat(appt_request.end_time.replace("Z", "+00:00")),
        title=title,
        external_event_id=created_event["event_id"],
        status=created_event["status"]
    )
    db.add(new_appointment)
    
    lead.status = "Appointment Set"
    lead.last_updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Appointment created successfully.", "appointment_details": created_event}
