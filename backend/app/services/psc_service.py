import requests
import os
from typing import Optional

class PSCService:
    """
    A service to interact with the SAM.gov PSC Public API to get descriptions for PSC codes.
    API documentation: https://open.gsa.gov/api/PSC-Public-API/
    """
    def __init__(self):
        self.base_url = "https://api.sam.gov/prod/locationservices/v1/api/publicpscdetails"
        self.api_key = os.getenv("SAM_GOV_API_KEY")

    def get_description_for_code(self, psc_code: str) -> Optional[str]:
        """
        Fetches the name/description for a given PSC code.

        Args:
            psc_code: The PSC code.

        Returns:
            The official name string if found, otherwise None.
        """
        if not self.api_key:
            print("PSC Service: SAM_GOV_API_KEY is not set. Cannot make API calls.")
            return None

        params = {
            'api_key': self.api_key,
            'searchBy': 'psc',
            'q': psc_code
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("totalRecords") != "0" and "productServiceCodeList" in data:
                # Return the name of the first result
                return data["productServiceCodeList"][0].get("pscName")
            else:
                print(f"PSC Service: No description found for PSC code '{psc_code}'.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"PSC Service: Could not connect to API: {e}")
            return None
        except Exception as e:
            print(f"PSC Service: An error occurred: {e}")
            return None 