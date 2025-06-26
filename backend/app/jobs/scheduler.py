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

def analyze_completed_conversations():
    """
    Finds completed leads that haven't been analyzed, analyzes their
    conversations, and stores the insights in the 'learnings' table.
    """
    print("Scheduler: Running 'analyze_completed_conversations' job...")
    db = SessionLocal()
    convo_service = ConversationService()
    
    try:
        # Find leads that are "done" (e.g., appointment set or disqualified)
        # and have not been analyzed yet.
        completed_leads = db.query(Lead).filter(
            Lead.status.in_(['Appointment Set', 'Disqualified']),
            Lead.analyzed_for_learning == False
        ).all()

        if not completed_leads:
            print("Scheduler: No new completed leads to analyze.")
            return

        for lead in completed_leads:
            print(f"Scheduler: Analyzing lead {lead.id}...")
            conversation_history = db.query(ConversationLog).filter(
                ConversationLog.lead_id == lead.id
            ).order_by(ConversationLog.timestamp).all()

            if not conversation_history:
                # Mark as analyzed even if there's no conversation to prevent re-checking
                lead.analyzed_for_learning = True
                db.commit()
                continue

            analysis = convo_service.analyze_conversation(conversation_history)

            # Store the learning
            new_learning = Learning(
                conversation_id=conversation_history[-1].id, # Link to the last log entry
                outcome_tag=analysis['outcome_tag'],
                summary=analysis['summary']
            )
            db.add(new_learning)

            # Mark the lead as analyzed
            lead.analyzed_for_learning = True
            db.commit()
            print(f"Scheduler: Successfully analyzed and stored learning for lead {lead.id}.")

    except Exception as e:
        print(f"Scheduler: An error occurred during analysis job: {e}")
        db.rollback()
    finally:
        db.close()

def detect_no_shows_and_follow_up():
    """
    Finds appointments that have passed their end time without being marked
    'completed' and triggers a follow-up.
    """
    print("Scheduler: Running 'detect_no_shows_and_follow_up' job...")
    db = SessionLocal()
    facebook_service = FacebookService()

    try:
        # Find appointments that ended in the last hour and are still 'confirmed'
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        potential_no_shows = db.query(Appointment).filter(
            Appointment.status == 'confirmed', # Or 'tentative'
            Appointment.end_time < now,
            Appointment.end_time > one_hour_ago
        ).all()

        if not potential_no_shows:
            print("Scheduler: No potential no-shows to process.")
            return

        for appt in potential_no_shows:
            lead = appt.lead
            print(f"Scheduler: Detected potential no-show for lead {lead.id}.")

            # Mock sending a follow-up message
            # A real conversation service would generate this text
            follow_up_message = "Hi there, it looks like we missed our meeting. I hope everything is alright. Please let me know if you'd like to reschedule."
            
            recipient_id = lead.business_name # Using placeholder
            facebook_service.send_direct_message(recipient_id, follow_up_message)

            # Log the follow-up
            new_log = ConversationLog(
                lead_id=lead.id,
                sender="AI",
                message=follow_up_message
            )
            db.add(new_log)

            # Update status
            lead.status = "No-Show Follow-up"
            appt.status = "no-show"
            db.commit()
            print(f"Scheduler: Sent no-show follow-up for lead {lead.id}.")

    except Exception as e:
        print(f"Scheduler: An error occurred during no-show detection job: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting background job scheduler...")
    # Schedule the jobs to run.
    schedule.every(1).hour.do(analyze_completed_conversations)
    schedule.every(1).hour.do(detect_no_shows_and_follow_up)
    
    # You can add other jobs here for Epic 5, like no-show detection.

    while True:
        schedule.run_pending()
        time.sleep(1)
