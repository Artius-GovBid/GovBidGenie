import schedule
import time
import sys
import os
from datetime import datetime, timedelta

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.client import SessionLocal
from app.db.models import Lead, ConversationLog, Learning, Appointment
from app.services.conversation_service import ConversationService
from app.services.facebook_service import FacebookService
from app.services.sam_service import SAMService
from app.services.lead_service import LeadService

def fetch_sam_opportunities_job():
    """
    Fetches new opportunities from SAM.gov and stores them, then creates leads.
    """
    print("Scheduler: Running 'fetch_sam_opportunities_job'...")
    with SessionLocal() as db:
        try:
            # Step 1: Fetch and store new opportunities
            sam_service = SAMService()
            sam_service.fetch_and_store_opportunities(db)
            print("Scheduler: SAM.gov fetch completed.")

            # Step 2: Process newly stored opportunities to create leads
            lead_service = LeadService(db)
            lead_service.process_new_opportunities()
            print("Scheduler: Lead creation process from opportunities completed.")

            print("Scheduler: 'fetch_sam_opportunities_job' completed successfully.")
        except Exception as e:
            print(f"Scheduler: An error occurred during SAM fetch job: {e}")
            db.rollback()

def analyze_completed_conversations():
    """
    Finds completed leads that haven't been analyzed, analyzes their
    conversations, and stores the insights in the 'learnings' table.
    """
    print("Scheduler: Running 'analyze_completed_conversations' job...")
    with SessionLocal() as db:
        conversation_service = ConversationService()
        try:
            completed_leads = db.query(Lead).filter(
                Lead.status.in_(['Appointment Set', 'Disqualified']),
                Lead.analyzed_for_learning.is_(False)
            ).all()

            if not completed_leads:
                print("Scheduler: No new completed leads to analyze.")
                return

            leads_to_update = []
            for lead in completed_leads:
                print(f"Scheduler: Analyzing lead {lead.id}...")
                conversation_logs = db.query(ConversationLog).filter(
                    ConversationLog.lead_id == lead.id
                ).order_by(ConversationLog.created_at).all()

                if not conversation_logs:
                    leads_to_update.append(lead.id)
                    continue

                history_for_analysis = [
                    {"sender": str(log.sender), "text": str(log.message)} for log in conversation_logs
                ]
                analysis = conversation_service.analyze_conversation(history_for_analysis)

                new_learning = Learning(
                    lead_id=lead.id,
                    outcome_tag=analysis.get('tag'),
                    summary=analysis.get('summary')
                )
                db.add(new_learning)
                leads_to_update.append(lead.id)

            # Bulk update analyzed leads
            if leads_to_update:
                db.query(Lead).filter(Lead.id.in_(leads_to_update)).update(
                    {"analyzed_for_learning": True}, synchronize_session=False
                )

            db.commit()
            print(f"Scheduler: Successfully processed {len(completed_leads)} leads.")

        except Exception as e:
            print(f"Scheduler: An error occurred during analysis job: {e}")
            db.rollback()

def detect_no_shows_and_follow_up():
    """
    Finds appointments that have passed their end time without being marked
    'completed' and triggers a follow-up.
    """
    print("Scheduler: Running 'detect_no_shows_and_follow_up' job...")
    with SessionLocal() as db:
        facebook_service = FacebookService()
        try:
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)

            potential_no_shows = db.query(Appointment).filter(
                Appointment.status == 'confirmed',
                Appointment.end_time < now,
                Appointment.end_time > one_hour_ago
            ).all()

            if not potential_no_shows:
                print("Scheduler: No potential no-shows to process.")
                return
            
            leads_to_update_status = []
            appointments_to_update_status = []

            for appointment in potential_no_shows:
                lead = appointment.lead
                if lead is None:
                    continue
                
                print(f"Scheduler: Detected potential no-show for lead {lead.id}.")

                follow_up_message = "Hi there, it looks like we missed our meeting. I hope everything is alright. Please let me know if you'd like to reschedule."
                
                if lead.business_name is not None:
                    facebook_service.send_direct_message(lead.business_name, follow_up_message)

                new_log = ConversationLog(
                    lead_id=lead.id,
                    sender="bot",
                    message=follow_up_message,
                    created_at=datetime.utcnow()
                )
                db.add(new_log)

                leads_to_update_status.append(lead.id)
                appointments_to_update_status.append(appointment.id)
            
            if leads_to_update_status:
                db.query(Lead).filter(Lead.id.in_(leads_to_update_status)).update(
                    {"status": "No-Show Follow-up"}, synchronize_session=False
                )
            
            if appointments_to_update_status:
                db.query(Appointment).filter(Appointment.id.in_(appointments_to_update_status)).update(
                    {"status": "no-show"}, synchronize_session=False
                )

            db.commit()
            print(f"Scheduler: Processed {len(potential_no_shows)} potential no-shows.")

        except Exception as e:
            print(f"Scheduler: An error occurred during no-show detection job: {e}")
            db.rollback()

if __name__ == "__main__":
    print("Starting background job scheduler...")
    # Schedule the jobs to run.
    schedule.every().day.at("01:00").do(fetch_sam_opportunities_job)
    schedule.every(1).hour.do(analyze_completed_conversations)
    schedule.every(1).hour.do(detect_no_shows_and_follow_up)
    
    # You can add other jobs here for Epic 5, like no-show detection.

    while True:
        schedule.run_pending()
        time.sleep(1)
