import os
import requests
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class SAMService:
    """
    Service to interact with the SAM.gov Opportunities API.
    """
    def __init__(self):
        self.api_key = os.environ.get("SAM_GOV_API_KEY") # Corrected environment variable name
        self.base_url = "https://api.sam.gov/prod/opportunities/v2/search"
        self.headers = {'Accept': 'application/json'}

    def fetch_opportunities(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Fetches a list of opportunities from the SAM.gov API.

        Args:
            params: A dictionary of query parameters to filter the results.
                    Example: {'postedFrom': 'MM/DD/YYYY', 'postedTo': 'MM/DD/YYYY', 'limit': 10}

        Returns:
            A list of opportunity dictionaries.
        """
        if params is None:
            params = {}

        # Add the API key to every request
        if self.api_key:
            params['api_key'] = self.api_key
        
        # If no date range is specified, default to the last 30 days
        if 'postedFrom' not in params and 'postedTo' not in params:
            today = datetime.now()
            thirty_days_ago = today - timedelta(days=30)
            params['postedTo'] = today.strftime('%Y-%m-%d')
            params['postedFrom'] = thirty_days_ago.strftime('%Y-%m-%d')

        try:
            # Use a GET request with all parameters in the URL
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            data = response.json()
            opportunities = data.get("opportunitiesData", [])
            
            return self._parse_opportunities(opportunities)

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to fetch data from SAM.gov. Error: {e}")
            return []
        except ValueError: # Catches JSON decoding errors
            print("ERROR: Failed to decode JSON response from SAM.gov.")
            return []

    def _parse_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parses the raw opportunity data from the API into a cleaner format.
        """
        parsed_list = []
        for opp in opportunities:
            posted_date_obj = None
            posted_date_str = opp.get("postedDate")
            if posted_date_str:
                try:
                    # The format seems to be 'YYYY-MM-DD'
                    posted_date_obj = datetime.strptime(posted_date_str, '%Y-%m-%d')
                except (ValueError, TypeError):
                    # It might also include time information
                    try:
                        posted_date_obj = datetime.fromisoformat(posted_date_str.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        print(f"Could not parse date: {posted_date_str}")

            parsed_opp = {
                "sam_gov_id": opp.get("solicitationId"),
                "title": opp.get("title"),
                "url": opp.get("fullGovtResponseLink", [{}])[0].get("url") if opp.get("fullGovtResponseLink") else None,
                "agency": opp.get("organizationHierarchy", {}).get("departmentName"),
                "posted_date": posted_date_obj
            }
            parsed_list.append(parsed_opp)
        return parsed_list

    def fetch_and_store_opportunities(self, db: "Session"):
        """
        Fetches opportunities from the SAM.gov API and stores them in the database.
        Prevents duplicates by checking the sam_gov_id.
        """
        from app.db.models import Opportunity
        from datetime import datetime, timedelta

        print("SAM Service: Starting to fetch and store opportunities...")
        
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        posted_from = yesterday.strftime('%m/%d/%Y')
        posted_to = today.strftime('%m/%d/%Y')

        params = {
            'limit': 100,
            'postedFrom': posted_from,
            'postedTo': posted_to
        }

        opportunities_data = self.fetch_opportunities(params=params)
        if not opportunities_data:
            print("SAM Service: No new opportunities found in the last 24 hours.")
            return

        new_opportunities_count = 0
        for opp_data in opportunities_data:
            sam_id = opp_data.get('sam_gov_id')
            if not sam_id:
                continue

            exists = db.query(Opportunity).filter(Opportunity.sam_gov_id == sam_id).first()
            if not exists:
                posted_date_obj = None
                if opp_data.get('posted_date'):
                    try:
                        posted_date_obj = datetime.strptime(opp_data['posted_date'], '%Y-%m-%d')
                    except (ValueError, TypeError):
                        continue
                
                new_opp = Opportunity(
                    sam_gov_id=sam_id,
                    title=opp_data.get('title'),
                    url=opp_data.get('url'),
                    agency=opp_data.get('agency'),
                    posted_date=posted_date_obj,
                    naics_code=opp_data.get('naicsCode'),
                    psc_code=opp_data.get('classificationCode')
                )
                db.add(new_opp)
                new_opportunities_count += 1
        
        if new_opportunities_count > 0:
            db.commit()
            print(f"SAM Service: Successfully stored {new_opportunities_count} new opportunities.")
        else:
            print("SAM Service: No new opportunities to store.")

# Example usage (for testing or direct script execution):
if __name__ == '__main__':
    service = SAMService()
    # Example: Get the 10 most recently posted opportunities
    recent_opportunities = service.fetch_opportunities(params={'limit': 10, 'sortBy': 'postedDate'})
    if recent_opportunities:
        for opp in recent_opportunities:
            print(f"Title: {opp['title']}\nAgency: {opp['agency']}\nURL: {opp['url']}\n")
    else:
        print("Could not retrieve opportunities.")
