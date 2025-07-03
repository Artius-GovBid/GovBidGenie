from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.db.client import get_db, SessionLocal
from app.db.models import Opportunity, Lead, ConversationLog, Appointment
from app.services.devops_service import DevOpsService
from app.services.facebook_service import FacebookService
from app.services.conversation_service import ConversationService
from app.services.calendar_service import CalendarService
from app.services.lead_service import LeadService

router = APIRouter()

# --- Pydantic Models for API data validation ---

class OpportunityCreate(BaseModel):
    sam_gov_id: str
    title: str
    url: HttpUrl
    agency: str
    posted_date: datetime

class LeadCreate(BaseModel):
    opportunity_id: int
    business_name: str
    facebook_page_url: HttpUrl

class IncomingMessage(BaseModel):
    message: str

class AppointmentRequest(BaseModel):
    start_time: str # ISO 8601 format
    end_time: str   # ISO 8601 format

class LeadCreateSchema(BaseModel):
    sam_gov_id: str
    title: str
    url: HttpUrl
    agency: str
    posted_date: datetime

# --- Background Task ---

def create_devops_work_item_task(lead_id: int):
    """
    Background task to create a DevOps work item and update the lead.
    It creates its own database session to operate independently.
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
            opportunity_url=str(opportunity.url),
            agency=opportunity.agency,
            source="SAM.gov"
        )
        
        if work_item and 'id' in work_item:
            ado_id = work_item['id']
            lead_service.update_lead_ado_id(lead.id, ado_id)
            print(f"BACKGROUND_TASK_SUCCESS: Created ADO work item {ado_id} for lead {lead.id}")
        else:
            print(f"BACKGROUND_TASK_ERROR: Failed to create ADO work item for lead {lead_id}. Response: {work_item}")
    
    except Exception as e:
        print(f"BACKGROUND_TASK_ERROR: An exception occurred for lead {lead_id}: {e}")
    finally:
        db.close()

# --- API Endpoints ---

@router.post("/", status_code=202, summary="Creates a new lead from a SAM.gov opportunity.")
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

    # Schedule the ADO work item creation to run in the background
    background_tasks.add_task(create_devops_work_item_task, new_lead.id)

    return {
        "message": "Lead creation accepted. Azure DevOps work item will be created in the background.",
        "lead_id": new_lead.id,
    }

@router.post("/prospect/{lead_id}", status_code=200, summary="Find a Facebook page for an identified lead.")
def prospect_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Takes an 'Identified' lead, searches Facebook for a matching business page
    using keywords from the associated opportunity, and updates the lead's
    details and status to 'Prospected'.
    """
    lead_query = db.query(Lead).filter(Lead.id == lead_id)
    lead = lead_query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead.status != "Identified":
        raise HTTPException(status_code=400, detail=f"Lead status is '{lead.status}', must be 'Identified'.")

    if not lead.opportunity:
        raise HTTPException(status_code=404, detail=f"Associated opportunity not found for lead {lead_id}")

    search_query = lead.opportunity.title

    facebook_service = FacebookService()
    page_id = facebook_service.find_page_by_name(search_query)

    if not page_id:
        lead_query.update({"status": "Prospecting Failed"})
        db.commit()
        raise HTTPException(status_code=404, detail=f"No matching Facebook pages found for query: '{search_query}'")

    page_info = facebook_service.get_page_info(page_id)
    if not page_info or 'name' not in page_info:
        lead_query.update({"status": "Prospecting Failed"})
        db.commit()
        raise HTTPException(status_code=500, detail="Found a page but could not retrieve its information.")

    # Update lead details using the update method
    update_data = {
        "business_name": page_info['name'],
        "facebook_page_url": f"https://www.facebook.com/{page_id}",
        "status": "Prospected",
        "last_updated_at": datetime.utcnow()
    }
    lead_query.update(update_data)
    
    db.commit()
    
    # Fetch the updated lead to return it
    updated_lead = db.query(Lead).filter(Lead.id == lead_id).first()

    return { "message": "Lead successfully prospected.", "lead": updated_lead }

@router.post("/engage/{lead_id}", status_code=200, summary="Perform the engagement sequence for a prospected lead.")
def engage_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Takes a 'Prospected' lead, runs the engagement sequence (like, share, comment),
    and updates the lead's status to 'Engaged'.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.status != "Prospected":
        raise HTTPException(status_code=400, detail=f"Lead status is '{lead.status}', not 'Prospected'.")

    if not lead.facebook_page_url:
        raise HTTPException(status_code=400, detail="Lead has no Facebook page URL to engage with.")

    facebook_service = FacebookService()
    # This is a conceptual action. The actual implementation might involve multiple API calls.
    # For now, we'll assume a single method call represents the sequence.
    # facebook_service.share_and_mention(...)
    print(f"Performing engagement for {lead.facebook_page_url}")


    db.query(Lead).filter(Lead.id == lead_id).update({ "status": "Engaged", "last_updated_at": datetime.utcnow() })
    db.commit()

    return {"message": f"Successfully engaged with lead {lead.id}."}

@router.post("/initiate-conversation/{lead_id}", status_code=200, summary="Sends the first message to an engaged lead.")
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
    
    if not lead.opportunity:
         raise HTTPException(status_code=400, detail="Lead has no opportunity to reference.")

    facebook_service = FacebookService()
    
    facebook_service.send_outreach_dm(
        recipient_id="placeholder_recipient_id", # This needs to be discovered
        commenter_name=str(lead.business_name),
        opportunity=lead.opportunity
    )
    
    # Log the sent message
    # ... logic to create ConversationLog ...
    
    db.query(Lead).filter(Lead.id == lead_id).update({"status": "Messaged", "last_updated_at": datetime.utcnow()})
    db.commit()

    return {"message": f"Initial message sent to lead {lead.id}."}

@router.post("/conversation-webhook/{lead_id}", status_code=200, summary="Handles incoming messages from a lead.")
def handle_conversation_message(lead_id: int, incoming_message: IncomingMessage, db: Session = Depends(get_db)):
    """
    This endpoint is a webhook to be called by an external service (e.g., a Facebook webhook handler)
    when a new message is received from a lead. It logs the message, gets a response from the AI,
    sends the response, and logs it.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_log = ConversationLog(lead_id=lead.id, sender="user", message=incoming_message.message, created_at=datetime.utcnow())
    db.add(user_log)
    db.commit()

    conversation_history_query = db.query(ConversationLog).filter(ConversationLog.lead_id == lead.id).order_by(ConversationLog.created_at).all()
    history_for_service = [{"sender": log.sender, "text": log.message} for log in conversation_history_query]
    
    conversation_service = ConversationService()
    ai_response_text = conversation_service.get_next_response(history_for_service)

    facebook_service = FacebookService()
    # The recipient ID needs to be managed correctly
    # facebook_service.send_direct_message(recipient_id, ai_response_text)

    ai_log = ConversationLog(lead_id=lead.id, sender="bot", message=ai_response_text, created_at=datetime.utcnow())
    db.add(ai_log)
    
    db.query(Lead).filter(Lead.id == lead_id).update({"last_updated_at": datetime.utcnow()})
    db.commit()

    return {"message": "Response sent successfully."}

@router.post("/offer-appointment/{lead_id}", status_code=200, summary="Get available calendar slots and offer them.")
def offer_appointment(lead_id: int, db: Session = Depends(get_db)):
    """
    Checks the calendar for available slots and constructs a message
    offering the times to the lead.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    calendar_service = CalendarService()
    available_slots = calendar_service.get_available_slots()

    if not available_slots:
        raise HTTPException(status_code=404, detail="No available appointment slots found.")

    conversation_service = ConversationService()
    offer_message = conversation_service.generate_appointment_offer(available_slots)

    facebook_service = FacebookService()
    # facebook_service.send_direct_message(recipient_id, offer_message)
    
    new_log = ConversationLog(lead_id=lead.id, sender="bot", message=offer_message, created_at=datetime.utcnow())
    db.add(new_log)
    db.commit()
    
    return {"message": "Appointment slots offered.", "slots_offered": available_slots}

@router.post("/book-appointment/{lead_id}", status_code=201, summary="Books a confirmed appointment.")
def book_appointment(lead_id: int, appointment_request: AppointmentRequest, db: Session = Depends(get_db)):
    """
    Books an appointment in the calendar based on the user's selected time,
    creates an appointment record in the database, and updates the lead's status.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    calendar_service = CalendarService()
    
    start_time = datetime.fromisoformat(appointment_request.start_time)
    end_time = datetime.fromisoformat(appointment_request.end_time)
    
    event_id = calendar_service.create_appointment(
        start_time=start_time,
        end_time=end_time,
        subject=f"Meeting with {str(lead.business_name)}"
    )

    if not event_id:
        raise HTTPException(status_code=500, detail="Failed to create calendar event.")
        
    new_appointment = Appointment(
        lead_id=lead.id,
        start_time=start_time,
        end_time=end_time,
        title=f"Meeting with {str(lead.business_name)}",
        status="confirmed",
        external_event_id=event_id
    )
    db.add(new_appointment)
    
    db.query(Lead).filter(Lead.id == lead_id).update({
        "status": "Appointment Set",
        "last_updated_at": datetime.utcnow()
    })
    
    db.commit()
    db.refresh(new_appointment)
    
    return {"message": "Appointment successfully booked.", "appointment_id": new_appointment.id, "external_event_id": event_id}

@router.post("/reschedule-appointment/{lead_id}", status_code=200, summary="Handles rescheduling of an appointment.")
def reschedule_appointment(lead_id: int, db: Session = Depends(get_db)):
    """
    Finds an existing appointment for a lead, cancels it, and then
    re-initiates the appointment offering process.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    existing_appointment = db.query(Appointment).filter(Appointment.lead_id == lead_id, Appointment.status == 'confirmed').first()
    if not existing_appointment:
        raise HTTPException(status_code=404, detail="No confirmed appointment found to reschedule.")
        
    calendar_service = CalendarService()
    
    # Cancel the old appointment
    if existing_appointment.external_event_id:
        calendar_service.cancel_appointment(existing_appointment.external_event_id)
        
    existing_appointment.status = 'cancelled'
    db.commit()
    
    # Re-offer new times
    return offer_appointment(lead_id, db)
