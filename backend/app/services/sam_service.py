import os
import requests
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

# Use proper logging
logger = logging.getLogger(__name__)

class SAMService:
    """
    Service to interact with the SAM.gov Opportunities API.
    """
    def __init__(self):
        self.api_key = os.environ.get("SAM_API_KEY")
        self.base_url = "https://api.sam.gov/prod/opportunities/v2/search"
        if not self.api_key:
            logger.warning("SAM_API_KEY environment variable is not set.")
        else:
            logger.info("SAM_API_KEY loaded successfully.")

    def fetch_opportunities(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Fetches a list of opportunities from the SAM.gov API.
        """
        if params is None:
            params = {}

        if self.api_key:
            params['api_key'] = self.api_key
        
        headers = {'Accept': 'application/json'}

        logger.info(f"Fetching opportunities with params: {params}")

        try:
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            opportunities = data.get("opportunitiesData", [])
            logger.info(f"API returned {len(opportunities)} opportunities.")
            
            return self._parse_opportunities(opportunities)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from SAM.gov. Status Code: {e.response.status_code if e.response else 'N/A'}. Response: {e.response.text if e.response else 'No response'}")
            return []
        except ValueError:
            logger.error("Failed to decode JSON response from SAM.gov.")
            return []

    def _parse_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parses the raw opportunity data from the API into a cleaner format.
        """
        # This function doesn't need to change, parsing seems okay.
        parsed_list = []
        for opp in opportunities:
            parsed_opp = {
                "sam_gov_id": opp.get("noticeId"),
                "title": opp.get("title"),
                "url": opp.get("fullGovtResponseLink", [{}])[0].get("url") if opp.get("fullGovtResponseLink") else None,
                "agency": opp.get("organizationHierarchy", {}).get("departmentName"),
                "posted_date": opp.get("postedDate"),
                "naics_code": opp.get("naicsCode"),
                "psc_code": opp.get("classificationCode")
            }
            parsed_list.append(parsed_opp)
        return parsed_list

    def fetch_and_store_opportunities(self, db: "Session"):
        """
        Fetches opportunities from the SAM.gov API and stores them in the database.
        """
        from app.db.models import Opportunity
        from datetime import datetime, timedelta

        logger.info("Starting to fetch and store opportunities...")
        
        today = datetime.now()
        yesterday = today - timedelta(days=7)
        posted_from = yesterday.strftime('%m/%d/%Y')
        posted_to = today.strftime('%m/%d/%Y')

        params = {
            'limit': 100,
            'postedFrom': posted_from,
            'postedTo': posted_to
        }

        opportunities_data = self.fetch_opportunities(params=params)
        if not opportunities_data:
            logger.info("No opportunities found to process.")
            return

        new_opportunities_count = 0
        for i, opp_data in enumerate(opportunities_data):
            sam_id = opp_data.get('sam_gov_id')
            logger.info(f"--- Processing opportunity {i+1}/{len(opportunities_data)}: sam_id={sam_id} ---")

            if not sam_id:
                logger.warning("Skipping record due to missing sam_gov_id.")
                continue

            exists = db.query(Opportunity).filter(Opportunity.sam_gov_id == sam_id).first()
            if exists:
                logger.info(f"Opportunity with sam_id {sam_id} already exists. Skipping.")
                continue
            
            # ** NEW DETAILED LOGGING **
            logger.info(f"Data for new opportunity: {opp_data}")

            # Validate required fields
            if not opp_data.get('title'):
                 logger.warning(f"Skipping opportunity {sam_id} due to missing title.")
                 continue

            posted_date_obj = None
            if opp_data.get('posted_date'):
                try:
                    # The API seems to return YYYY-MM-DD
                    posted_date_obj = datetime.strptime(opp_data['posted_date'], '%Y-%m-%d')
                except (ValueError, TypeError) as e:
                    logger.error(f"Could not parse posted_date '{opp_data['posted_date']}' for sam_id {sam_id}. Error: {e}. Skipping.")
                    continue
            
            new_opp = Opportunity(
                sam_gov_id=opp_data.get("sam_gov_id"),
                title=opp_data.get('title'),
                url=opp_data.get('url'),
                agency=opp_data.get('agency'),
                posted_date=posted_date_obj,
                naics_code=opp_data.get('naics_code'),
                psc_code=opp_data.get('psc_code')
            )
            db.add(new_opp)
            new_opportunities_count += 1
            logger.info(f"Successfully staged opportunity {sam_id} for addition.")
        
        if new_opportunities_count > 0:
            db.commit()
            logger.info(f"Successfully committed {new_opportunities_count} new opportunities to the database.")
        else:
            logger.info("No new opportunities were ultimately stored (they may already exist or failed validation).")