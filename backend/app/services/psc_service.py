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

    async def process_new_opportunities(self):
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

            search_terms = []
            
            # Attempt 1: Use the opportunity title
            if opportunity.title:
                logger.info(f"Using opportunity title as a search term: '{opportunity.title}'")
                search_terms.append(opportunity.title)

            # Attempt 2: Fallback to NAICS code description
            naics_code = str(opportunity.naics_code) if opportunity.naics_code is not None else None
            if naics_code:
                logger.info(f"Attempting to find NAICS description for code {naics_code}...")
                naics_description = await self.naics_service.get_description(naics_code)
                if naics_description:
                    logger.info(f"Found NAICS description: '{naics_description}'")
                    search_terms.append(naics_description)
            
            # Attempt 3: Fallback to PSC code description
            psc_code = str(opportunity.psc_code) if opportunity.psc_code is not None else None
            if psc_code:
                logger.info(f"Attempting to find PSC description for code {psc_code}...")
                psc_description = await self.psc_service.get_description(psc_code)
                if psc_description:
                    logger.info(f"Found PSC description: '{psc_description}'")
                    search_terms.append(psc_description)

            if not search_terms:
                logger.warning(f"Could not determine a search term for opportunity {opportunity.id}. Skipping.")
                continue

            # Find the Facebook Page ID using the determined search term
            for term in search_terms:
                logger.info(f"Searching Facebook for pages matching '{term}'...")
                page_info = await self.facebook_service.find_page_by_name(term)

                if not page_info:
                    logger.warning(f"Could not find a Facebook page for '{term}' for opportunity {opportunity.id}.")
                    continue
                
                # Check if a lead for this opportunity and business already exists
                existing_lead = self.db.query(Lead).filter(
                    Lead.opportunity_id == opportunity.id,
                    Lead.business_name == page_info['name']
                ).first()

                if existing_lead:
                    logger.info(f"Lead already exists for opportunity {opportunity.id} and business '{page_info['name']}'.")
                    continue

                # Create a Lead record to track this outreach
                new_lead = Lead(
                    opportunity_id=opportunity.id,
                    status="Discovered",
                    facebook_page_url=page_info.get('link'),
                    business_name=page_info.get('name')
                )
                self.db.add(new_lead)
                self.db.commit()
                logger.info(f"Successfully created lead for opportunity {opportunity.id} targeting page {page_info.get('link')}.")
                # We found a lead for this opportunity, so we can move to the next one
                break

        logger.info("Finished processing opportunities.")