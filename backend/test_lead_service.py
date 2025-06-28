# Intentionally blank file to be populated in the next step. 

import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)

from app.services.lead_service import LeadService
from app.db.models import Opportunity, Lead

class TestLeadService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh LeadService with mocked dependencies for each test.
        """
        self.mock_db_session = MagicMock()
        
        # Mock the services that LeadService depends on
        self.mock_naics_service = MagicMock()
        self.mock_psc_service = MagicMock()
        self.mock_facebook_service = MagicMock()

        # Patch the services in the LeadService's namespace
        patcher_naics = patch('app.services.lead_service.NAICSService', return_value=self.mock_naics_service)
        patcher_psc = patch('app.services.lead_service.PSCService', return_value=self.mock_psc_service)
        patcher_facebook = patch('app.services.lead_service.FacebookService', return_value=self.mock_facebook_service)

        # Start the patchers
        self.addCleanup(patcher_naics.stop)
        self.addCleanup(patcher_psc.stop)
        self.addCleanup(patcher_facebook.stop)
        
        patcher_naics.start()
        patcher_psc.start()
        patcher_facebook.start()
        
        # Instantiate the service with the mocked session
        self.lead_service = LeadService(self.mock_db_session)

    def test_process_new_opportunities_logic(self):
        """
        Test the full logic of processing a new opportunity, including fallback.
        """
        # --- SCENARIO 1: Success with Title ---
        mock_opportunity_1 = Opportunity(id=1, title="Good Title", naics_code="111")
        self.mock_db_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [mock_opportunity_1]
        self.mock_facebook_service.find_page_by_name.return_value = "http://facebook.com/good_title_page"

        self.lead_service.process_new_opportunities()
        self.mock_facebook_service.find_page_by_name.assert_called_once_with("Good Title")
        self.mock_db_session.add.assert_called_once()
        self.assertEqual(self.mock_db_session.add.call_args[0][0].facebook_page_url, "http://facebook.com/good_title_page")
        self.mock_db_session.commit.assert_called_once()

        # --- SCENARIO 2: Fallback to NAICS ---
        # Reset mocks for the next scenario
        self.setUp() 

        mock_opportunity_2 = Opportunity(id=2, title="Vague Title", naics_code="541511")
        self.mock_db_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [mock_opportunity_2]
        self.mock_naics_service.get_description_for_code.return_value = "NAICS Description"
        self.mock_facebook_service.find_page_by_name.side_effect = [None, "http://facebook.com/naics_page"]

        self.lead_service.process_new_opportunities()
        self.assertEqual(self.mock_facebook_service.find_page_by_name.call_count, 2)
        self.mock_facebook_service.find_page_by_name.assert_any_call("Vague Title")
        self.mock_facebook_service.find_page_by_name.assert_any_call("NAICS Description")
        self.mock_db_session.add.assert_called_once()
        self.assertEqual(self.mock_db_session.add.call_args[0][0].facebook_page_url, "http://facebook.com/naics_page")


if __name__ == '__main__':
    unittest.main() 