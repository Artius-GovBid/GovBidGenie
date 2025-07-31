import logging
from sqlalchemy.orm import Session
from app.db.models import Opportunity, Lead
from app.services.facebook_service import FacebookService
from app.services.naics_service import NAICSService
from app.services.psc_service import PSCService
from app.services.sam_service import SAMService
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeadService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.facebook_service = FacebookService()
        self.naics_service = NAICSService()
        self.psc_service = PSCService()
        self.sam_service = SAMService()

    def get_lead_by_sam_id(self, sam_gov_id: str) -> Lead | None:
        """
        Retrieves a lead by its SAM.gov ID.
        """
        return self.db.query(Lead).join(Opportunity).filter(Opportunity.sam_gov_id == sam_gov_id).first()

    def create_lead(self, sam_gov_id: str, title: str, url: str, agency: str, posted_date: datetime) -> Lead:
        """
        Creates an opportunity and a corresponding lead.
        """
        # First, create the opportunity
        opportunity = Opportunity(
            sam_gov_id=sam_gov_id,
            title=title,
            url=url,
            agency=agency,
            posted_date=posted_date
        )
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)

        # Now, create the lead
        new_lead = Lead(
            opportunity_id=opportunity.id,
            status="IDENTIFIED"
        )
        self.db.add(new_lead)
        self.db.commit()
        self.db.refresh(new_lead)
        return new_lead

    def update_lead_ado_id(self, lead_id: int, ado_id: int):
        """
        Updates a lead with the Azure DevOps work item ID.
        """
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            lead.azure_devops_work_item_id = ado_id
            self.db.commit()

    def process_new_opportunities(self):
        """
        Processes new opportunities that haven't been converted into leads yet.
        """
        logger.info("Starting to process new opportunities...")
        
        unprocessed_opportunities = self.db.query(Opportunity).outerjoin(Lead).filter(Lead.id == None).all()

        if not unprocessed_opportunities:
            logger.info("No new opportunities to process.")
            return

        logger.info(f"Found {len(unprocessed_opportunities)} new opportunities to process.")
        
        for opportunity in unprocessed_opportunities:
            logger.info(f"Processing opportunity ID {opportunity.id}: '{opportunity.title}'")

            search_term = None
            
            # Attempt 1: Use the opportunity title
            if opportunity.title:
                logger.info(f"Attempting to find search term with Opportunity Title: '{opportunity.title}'")
                search_term = opportunity.title # Use the title directly as the search term

            # Attempt 2: Fallback to NAICS code description
            if not search_term:
                naics_code = str(opportunity.naics_code) if opportunity.naics_code is not None else None
                if naics_code:
                    logger.info(f"Title search failed. Attempting with NAICS code {naics_code}...")
                    search_term = self.naics_service.get_description_for_code(naics_code)
                    if search_term:
                        logger.info(f"Found NAICS description: '{search_term}'")

            # Attempt 3: Fallback to PSC code description
            if not search_term:
                psc_code = str(opportunity.psc_code) if opportunity.psc_code is not None else None
                if psc_code:
                    logger.info(f"NAICS lookup failed. Attempting with PSC code {psc_code}...")
                    search_term = self.psc_service.get_description_for_code(psc_code)
                    if search_term:
                        logger.info(f"Found PSC description: '{search_term}'")

            if not search_term:
                logger.warning(f"Could not determine a search term for opportunity {opportunity.id}. Skipping.")
                continue

            # Find the Facebook Page ID using the determined search term
            logger.info(f"Searching Facebook for pages matching '{search_term}'...")
            target_page = self.facebook_service.find_page_by_name(search_term)

            if not target_page:
                logger.warning(f"Could not find a Facebook page for '{search_term}' for opportunity {opportunity.id}. Skipping.")
                continue

            page_id = target_page['id']
            page_name = target_page['name']
            page_url = f"https://www.facebook.com/{page_id}"

            # Create a Lead record to track this outreach
            new_lead = Lead(
                opportunity_id=opportunity.id,
                status="Prospected",
                facebook_page_url=page_url,
                business_name=page_name
            )
            self.db.add(new_lead)
            self.db.commit()
            logger.info(f"Successfully created lead for opportunity {opportunity.id} targeting page {page_id}.")

        logger.info("Finished processing opportunities.")

    def process_comment(self, comment_text: str, user_id: str, comment_id: str):
        """
        Processes a new comment, finds a relevant opportunity, creates a lead,
        and sends a private reply.
        """
        logger.info(f"Processing comment from user {user_id}: '{comment_text}'")

        # 1. Extract keywords from comment
        stop_words = {'i', 'am', 'looking', 'for', 'a', 'an', 'the', 'in', 'on', 'of', 'and', 'is', 'are'}
        keywords = [word.strip('.,!?;:') for word in comment_text.lower().split() if word.lower() not in stop_words]
        search_query = " ".join(keywords)

        if not search_query:
            logger.info(f"No usable keywords found in comment: '{comment_text}'")
            return

        # 2. Find the best NAICS code for the keywords
        logger.info(f"Finding NAICS code for keywords: '{search_query}'")
        naics_code = self.naics_service.find_code_for_keywords(search_query)

        if not naics_code:
            logger.info(f"No NAICS code found for keywords: '{search_query}'")
            return

        logger.info(f"Found NAICS code {naics_code}. Searching SAM.gov for opportunities.")

        # 3. Find a relevant opportunity on SAM.gov using the NAICS code
        opportunities = self.sam_service.fetch_opportunities(params={'naics': naics_code, 'limit': 1})
        if not opportunities:
            logger.info(f"No opportunities found for NAICS code: '{naics_code}'")
            return

        opportunity_data = opportunities[0]
        if not opportunity_data.get('sam_gov_id'):
            logger.warning("Opportunity data is missing sam_gov_id. Skipping.")
            return
        
        # 4. Check if an opportunity for this sam_gov_id already exists, or create it
        opportunity = self.db.query(Opportunity).filter(Opportunity.sam_gov_id == opportunity_data['sam_gov_id']).first()
        if not opportunity:
            # Ensure posted_date is a datetime object if it exists
            if 'posted_date' in opportunity_data and isinstance(opportunity_data['posted_date'], str):
                try:
                    opportunity_data['posted_date'] = datetime.fromisoformat(opportunity_data['posted_date'].replace('Z', '+00:00'))
                except ValueError:
                    opportunity_data['posted_date'] = None # or handle error appropriately

            opportunity = Opportunity(**opportunity_data)
            self.db.add(opportunity)
            self.db.commit()
            self.db.refresh(opportunity)
            logger.info(f"Created new opportunity: {opportunity.title}")
        
        # 5. Get user's name from their profile
        user_profile = self.facebook_service.get_user_profile(user_id)
        user_name = user_profile.get('name', 'there') if user_profile else 'there'

        # 6. Create the Lead
        new_lead = Lead(
            opportunity_id=opportunity.id,
            status="ENGAGED", # User has engaged with us
            business_name=user_name, # A good default
        )
        self.db.add(new_lead)
        self.db.commit()
        self.db.refresh(new_lead)
        logger.info(f"Created new lead {new_lead.id} for user {user_name}")
        
        # 7. Send a private reply to the comment
        message = (
            f"Hi {user_name}, thanks for your comment! Based on what you said, "
            f"I found a government contract opportunity you might be perfect for: '{opportunity.title}'. "
            f"You can see the details here: {opportunity.url}. "
            "Would you be interested in learning more?"
        )
        
        try:
            self.facebook_service.send_private_reply(comment_id, message)
            logger.info(f"Successfully sent private reply to comment {comment_id}")
            # Update lead status after successful message
            new_lead.status = "MESSAGED"
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to send private reply to comment {comment_id}: {e}") 