import logging
from sqlalchemy.orm import sessionmaker
from app.db.models import Opportunity, Lead
from app.services.facebook_service import FacebookService
from app.services.naics_service import NAICSService
# from app.services.psc_service import PSCService # Temporarily remove
from datetime import datetime

print(f"--- LOADING LEAD SERVICE FROM: {__file__} ---")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeadService:
    def __init__(self, db_session_factory: sessionmaker, facebook_service: FacebookService, naics_service: NAICSService): #, psc_service: PSCService):
        self.db_session_factory = db_session_factory
        self.facebook_service = facebook_service
        self.naics_service = naics_service
        # self.psc_service = psc_service

    def get_lead_by_sam_id(self, sam_gov_id: str):
        """
        Retrieves a lead by its SAM.gov ID.
        """
        with self.db_session_factory() as db:
            return db.query(Lead).join(Opportunity).filter(Opportunity.sam_gov_id == sam_gov_id).first()

    def create_lead(self, opportunity_id: int, business_name: str, page_id: str):
        """
        Creates a new Lead record.
        """
        with self.db_session_factory() as db:
            new_lead = Lead(
                opportunity_id=opportunity_id,
                status="Discovered",
                facebook_page_url=f"https://www.facebook.com/{page_id}",
                business_name=business_name,
                facebook_page_id=page_id
            )
            db.add(new_lead)
            db.commit()
            db.refresh(new_lead)
            logger.info(f"Successfully created lead for opportunity {opportunity_id} targeting page {business_name}.")
            return new_lead

    def update_lead_ado_id(self, lead_id: int, ado_id: int):
        """
        Updates a lead with the Azure DevOps work item ID.
        """
        with self.db_session_factory() as db:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                lead.azure_devops_work_item_id = ado_id
                db.commit()

    async def process_new_opportunities(self):
        """
        Processes new opportunities that haven't been converted into leads yet.
        """
        logger.info("Starting to process new opportunities...")
        
        with self.db_session_factory() as db:
            unprocessed_opportunities = db.query(Opportunity).outerjoin(Lead).filter(Lead.id == None).all()

            if not unprocessed_opportunities:
                logger.info("No new opportunities to process.")
                return

            logger.info(f"Found {len(unprocessed_opportunities)} new opportunities to process.")
        
        for opportunity in unprocessed_opportunities:
            logger.info(f"Processing opportunity ID {opportunity.id}: '{opportunity.title}'")

            search_terms = []
            
            # Use title first
            if opportunity.title:
                search_terms.append(opportunity.title)

            # Fallback to NAICS code description
            naics_code = str(opportunity.naics_code) if opportunity.naics_code is not None else None
            if naics_code:
                try:
                    naics_description = await self.naics_service.get_description(naics_code)
                    if naics_description:
                        search_terms.append(naics_description)
                except Exception as e:
                    logger.error(f"Error fetching NAICS description for {naics_code}: {e}")
            
            # Fallback to PSC code description - REMOVED FOR NOW
            # psc_code = str(opportunity.psc_code) if opportunity.psc_code is not None else None
            # if psc_code:
            #     try:
            #         psc_description = self.psc_service.get_description(psc_code)
            #         if psc_description:
            #             search_terms.append(psc_description)
            #     except Exception as e:
            #         logger.error(f"Error fetching PSC description for {psc_code}: {e}")

            if not search_terms:
                logger.warning(f"Could not determine a search term for opportunity {opportunity.id}. Skipping.")
                continue

            for term in search_terms:
                page_id = None
                try:
                    page_id = self.facebook_service.find_page_by_name(term)
                    if not page_id: continue
                    
                    page_info = self.facebook_service.get_page_info(page_id)
                    business_name = page_info.get('name') if page_info else None

                    if not business_name:
                        logger.warning(f"Could not extract business name from page info for term '{term}'. Skipping.")
                        continue

                    with self.db_session_factory() as db:
                        existing_lead = db.query(Lead).filter(
                            Lead.opportunity_id == opportunity.id,
                            Lead.business_name == business_name
                        ).first()

                        if existing_lead:
                            logger.info(f"Lead already exists for opportunity {opportunity.id} and business '{business_name}'.")
                            continue
                    
                    self.create_lead(opportunity.id, business_name, page_id)
                    break # Move to next opportunity once a lead is created
                
                except Exception as e:
                    logger.error(f"Error processing search term '{term}' for opportunity {opportunity.id}: {e}")
                    continue

        logger.info("Finished processing opportunities.")
 