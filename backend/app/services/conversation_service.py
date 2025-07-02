import logging
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Lead
from app.services.facebook_service import FacebookService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationService:
    """
    Manages sending outreach messages to potential leads via Facebook.
    """
    def __init__(self, db_session_factory: sessionmaker, facebook_service: FacebookService):
        self.db_session_factory = db_session_factory
        self.facebook_service = facebook_service

    def initiate_conversation(self, lead: Lead):
        """
        Sends a personalized outreach DM to the Facebook Page associated with a lead.
        """
        if not lead.opportunity:
            logger.error(f"Lead {lead.id} is missing associated opportunity data. Cannot initiate conversation.")
            return

        if not lead.facebook_page_id:
            logger.error(f"Lead {lead.id} is missing a Facebook Page ID. Cannot initiate conversation.")
            return

        logger.info(f"Initiating conversation for lead {lead.id} with page ID {lead.facebook_page_id}.")

        try:
            opportunity = lead.opportunity
            message = (
                f"Hello {lead.business_name}, my name is Genie.\n\n"
                f"I found a U.S. government contract opportunity that seems like a strong match for your business. "
                f"It's for '{opportunity.title}' with the {opportunity.agency}.\n\n"
                f"You can view the full details here: {opportunity.url}\n\n"
                "Would you be open to a brief chat about how we can help you win this contract?"
            )

            response = self.facebook_service.send_direct_message(
                recipient_page_id=lead.facebook_page_id,
                message=message
            )
            return response
        except Exception as e:
            logger.error(f"An unexpected error occurred while initiating conversation for lead {lead.id}: {e}")
            return None

    def process_discovered_leads(self):
        """
        Finds leads that have been discovered but not yet contacted and initiates
        a conversation with them.
        """
        with self.db_session_factory() as db:
            try:
                leads_to_contact = db.query(Lead).filter(Lead.status == "Discovered").all()
                if not leads_to_contact:
                    logger.info("ConversationService: No new leads to contact.")
                    return

                logger.info(f"ConversationService: Found {len(leads_to_contact)} leads to contact.")
                for lead in leads_to_contact:
                    response = self.initiate_conversation(lead)
                    if response and response.get('message_id'):
                        logger.info(f"Successfully sent message for lead {lead.id}. Message ID: {response['message_id']}")
                        lead.status = "CONTACTED"
                    else:
                        logger.error(f"Failed to send message for lead {lead.id}. Response: {response}")
                        lead.status = "CONTACT_FAILED"
                db.commit()
            except Exception as e:
                logger.error(f"An error occurred in process_discovered_leads: {e}")
                db.rollback()