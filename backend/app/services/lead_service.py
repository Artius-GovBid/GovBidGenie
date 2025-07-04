import logging
from sqlalchemy.orm import Session
from app.db.models import Opportunity, Lead
from app.services.facebook_service import FacebookService
from app.services.naics_service import NAICSService
from app.services.psc_service import PSCService
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