import httpx
from typing import Optional

class NAICSService:
    """
    A service to interact with a public API to get descriptions for NAICS codes.
    Uses the API from https://github.com/codeforamerica/naics-api
    """
    def __init__(self):
        self.base_url = "http://api.naics.us/v0/q"

    async def get_description(self, naics_code: str) -> Optional[str]:
        """
        Fetches the title/description for a given NAICS code asynchronously.

        Args:
            naics_code: The 6-digit NAICS code.

        Returns:
            The official title string if found, otherwise None.
        """
        # The API works with 2012-2022 codes. We'll use a recent year.
        params = {'year': '2012', 'code': naics_code}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # The API returns a list, we want the title of the first item
                if isinstance(data, list) and data:
                    return data[0].get('title')
                # Sometimes it returns a single dictionary
                elif isinstance(data, dict):
                    return data.get('title')
                else:
                    return None
            except httpx.HTTPStatusError as e:
                print(f"NAICS Service: Could not connect to API: {e}")
                return None
            except Exception as e:
                print(f"NAICS Service: An error occurred: {e}")
                return None 