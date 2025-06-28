import os
import requests
from typing import List, Dict, Any, Optional

class SAMService:
    """
    Service to interact with the SAM.gov Opportunities API.
    """
    def __init__(self):
        self.api_key = os.environ.get("SAM_API_KEY") # Placeholder for API key
        self.base_url = "https://api.sam.gov/prod/opportunities/v2/search"

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

        # The SAM.gov API requires an api_key for many queries, but we'll make a basic one without it first.
        # If an API key is provided, add it to the params.
        if self.api_key:
            params['api_key'] = self.api_key
        
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.base_url, json=params, headers=headers)
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
            parsed_opp = {
                "sam_gov_id": opp.get("solicitationId"),
                "title": opp.get("title"),
                "url": opp.get("fullGovtResponseLink", [{}])[0].get("url") if opp.get("fullGovtResponseLink") else None,
                "agency": opp.get("organizationHierarchy", {}).get("departmentName"),
                "posted_date": opp.get("postedDate")
            }
            parsed_list.append(parsed_opp)
        return parsed_list

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
