import logging
from sqlalchemy.orm import Session
from app.db.models import Lead, Opportunity
from app.services.facebook_service import FacebookService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationService:
    """
    Manages sending outreach messages to potential leads via Facebook.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        self.facebook_service = FacebookService()

    def initiate_conversation(self, lead: Lead):
        """
        Sends a personalized outreach DM to the Facebook Page associated with a lead.

        Args:
            lead: The Lead object containing the opportunity and business info.
        """
        if not lead.opportunity:
            logger.error(f"Lead {lead.id} is missing associated opportunity data. Cannot initiate conversation.")
            return

        if not lead.facebook_page_id:
            logger.error(f"Lead {lead.id} is missing a Facebook Page ID. Cannot initiate conversation.")
            return

        logger.info(f"Initiating conversation for lead {lead.id} with page ID {lead.facebook_page_id}.")

        try:
            # Construct a compelling, personalized message
            opportunity = lead.opportunity
            message = (
                f"Hello {lead.business_name}, my name is Genie.\n\n"
                f"I found a U.S. government contract opportunity that seems like a strong match for your business. "
                f"It's for '{opportunity.title}' with the {opportunity.agency}.\n\n"
                f"You can view the full details here: {opportunity.url}\n\n"
                "Would you be open to a brief chat about how we can help you win this contract?"
            )

            # Use the Facebook service to send the message
            response = self.facebook_service.send_direct_message(
                recipient_page_id=lead.facebook_page_id,
                message=message
            )

            if response and response.get('message_id'):
                logger.info(f"Successfully sent message for lead {lead.id}. Message ID: {response['message_id']}")
                # Update the lead's status to show we've made contact
                # To update, we need to query for the lead object in this session
                lead_to_update = self.db.query(Lead).filter(Lead.id == lead.id).first()
                if lead_to_update:
                    lead_to_update.status = "CONTACTED"
                    self.db.commit()
                    logger.info(f"Updated lead {lead.id} status to CONTACTED.")
            else:
                logger.error(f"Failed to send message for lead {lead.id}. Response: {response}")

        except Exception as e:
            logger.error(f"An unexpected error occurred while initiating conversation for lead {lead.id}: {e}")
            # Optionally, you could set the lead status to "CONTACT_FAILED"
            # lead.status = "CONTACT_FAILED"
            # self.db.commit()
