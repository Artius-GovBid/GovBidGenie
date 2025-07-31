import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    """Mocks the database session to prevent actual database calls."""
    with patch("app.db.client.get_db") as mock_get_db:
        mock_session = MagicMock()
        mock_get_db.return_value = mock_session
        yield mock_session

def test_handle_facebook_webhook_valid_comment(mock_db_session):
    """
    Tests the Facebook webhook endpoint with a valid new comment event.
    """
    # Arrange: Mock the LeadService and its process_comment method
    with patch("app.api.v1.endpoints.webhooks.LeadService") as mock_lead_service:
        mock_instance = mock_lead_service.return_value
        
        # The payload simulates a new comment on a feed post
        payload = {
            "object": "page",
            "entry": [{
                "id": "123456789",
                "time": 1622546359,
                "changes": [{
                    "field": "feed",
                    "value": {
                        "item": "comment",
                        "verb": "add",
                        "comment_id": "987654321",
                        "from": {"id": "user123", "name": "Test User"},
                        "message": "This is a test comment"
                    }
                }]
            }]
        }

        # Act: Send a POST request to the webhook endpoint
        response = client.post("/api/v1/webhooks/facebook", json=payload)

        # Assert: Check that the response is successful and the service was called
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
        # Verify that LeadService was initialized with the db session
        mock_lead_service.assert_called_once_with(mock_db_session)
        
        # Verify that process_comment was called with the correct data
        mock_instance.process_comment.assert_called_once_with(
            comment_text="This is a test comment",
            user_id="user123",
            comment_id="987654321"
        )
