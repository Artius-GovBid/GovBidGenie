import csv
import os
from typing import Optional, List

class NAICSService:
    """
    A service to find NAICS codes and descriptions from a local CSV file.
    """
    def __init__(self):
        self.naics_data = []
        # Correctly locate the CSV file relative to this script's location
        dir_path = os.path.dirname(os.path.realpath(__file__))
        csv_path = os.path.join(dir_path, 'naics_codes.csv')
        
        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as infile:
                # Use DictReader to make it easy to access columns by name
                reader = csv.DictReader(infile)
                for row in reader:
                    self.naics_data.append(row)
        except FileNotFoundError:
            print(f"ERROR: Could not find the NAICS data file at {csv_path}")
        except Exception as e:
            print(f"ERROR: Failed to load NAICS data: {e}")

    def find_code_for_keywords(self, keywords: str) -> Optional[str]:
        """
        Searches for the most relevant NAICS code for a given set of keywords
        using a scoring system.

        Args:
            keywords: A string of keywords to search for.

        Returns:
            The most relevant 6-digit NAICS code as a string, or None if not found.
        """
        if not self.naics_data:
            return None

        search_keywords = set(keywords.lower().split())
        best_match_code = None
        highest_score = 0

        for row in self.naics_data:
            # Ensure we are looking at 6-digit codes for specificity
            code = row.get('Code')
            if not code or len(code) != 6:
                continue

            description = row.get('Class title', '').lower()
            if not description:
                continue
            
            score = 0
            # 1. Simple keyword match score
            matched_keywords = search_keywords.intersection(description.split())
            score += len(matched_keywords)

            # 2. Bonus for full phrase match
            if keywords.lower() in description:
                score += 5 # A big bonus for a direct phrase match

            if score > highest_score:
                highest_score = score
                best_match_code = code
        
        return best_match_code

    def get_description_for_code(self, naics_code: str) -> Optional[str]:
        """
        Fetches the title/description for a given NAICS code from local data.
        """
        if not self.naics_data:
            return None
            
        for row in self.naics_data:
            if row.get('Code') == naics_code:
                return row.get('Class title')
        
        return None 