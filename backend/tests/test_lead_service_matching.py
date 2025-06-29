import unittest
import sys
import os
from unittest.mock import patch, MagicMock, ANY
from sqlalchemy.orm import Session

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.lead_service import LeadService
from app.db.models import Opportunity, Lead

class TestLeadServiceMatching(unittest.TestCase):

    @patch('app.services.lead_service.DevOpsService')
    @patch('app.services.lead_service.FacebookService')
    def test_finds_best_match_and_creates_lead(self, MockFacebookService, MockDevOpsService):
        # 1. Setup
        mock_db = MagicMock(spec=Session)
        
        mock_opportunities = [
            Opportunity(id=1, title="Roofing Contract for Federal Building", agency="GSA", url="http://example.com/roofing"),
            Opportunity(id=2, title="Cybersecurity Services for USDA", agency="USDA", url="http://example.com/cyber"),
            Opportunity(id=3, title="Janitorial Services for Local Office", agency="Local Gov", url="http://example.com/janitorial")
        ]
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = mock_opportunities
        
        mock_facebook_instance = MockFacebookService.return_value
        mock_facebook_instance.get_page_info.return_value = {'name': 'TBs Roofing and Construction'}
        
        mock_devops_instance = MockDevOpsService.return_value

        # 2. Execution
        lead_service = LeadService(mock_db)
        lead_service.find_and_create_lead_from_comment(commenter_id="page_id_123", comment_text="Great post!")

        # 3. Assertions
        # Assert that a new lead was created
        mock_db.add.assert_called_once()
        created_lead = mock_db.add.call_args[0][0]
        self.assertIsInstance(created_lead, Lead)
        self.assertEqual(created_lead.opportunity_id, 1) # Should match the roofing contract
        self.assertEqual(created_lead.status, "Identified_By_Genie")

        # Assert that the DevOps service was called with the new lead
        mock_devops_instance.create_work_item_from_lead.assert_called_once_with(created_lead, mock_db)

if __name__ == '__main__':
    unittest.main() 