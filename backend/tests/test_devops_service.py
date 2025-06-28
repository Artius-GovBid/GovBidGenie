import unittest
from unittest.mock import patch, Mock
import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)

from app.services.devops_service import DevOpsService

class TestDevOpsService(unittest.TestCase):

    @patch.dict(os.environ, {"ADO_ORG_URL": "https://dev.azure.com/testorg", "ADO_PAT": "testpat"})
    @patch('requests.post')
    def test_create_work_item_sends_correct_initial_state(self, mock_post):
        """
        Verify that create_work_item sends the correct initial state ("Identified").
        """
        # Configure the mock to return a successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": 123, "rev": 1}
        mock_post.return_value = mock_response

        # Instantiate the service and call the method
        service = DevOpsService()
        service.create_work_item(
            title="New Lead: Test",
            opportunity_url="http://test.com",
            agency="Test Agency",
            source="Test Source"
        )

        # Verify that requests.post was called
        self.assertTrue(mock_post.called)

        # Check the payload sent to the API
        call_args, call_kwargs = mock_post.call_args
        sent_payload = call_kwargs.get("json", [])
        
        # Find the operation that sets the state
        state_op = next((op for op in sent_payload if op.get("path") == "/fields/System.State"), None)

        # Assert that the state was set, and set to "Identified"
        self.assertIsNotNone(state_op)
        self.assertEqual(state_op.get("value"), "Identified")


if __name__ == '__main__':
    unittest.main() 