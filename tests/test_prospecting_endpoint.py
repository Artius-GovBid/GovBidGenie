import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

from app.main import app
from app.db.models import Lead, Opportunity, Base
from app.db.client import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_prospecting.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Pytest Fixture ---
@pytest.fixture(scope="function")
def db_session():
    """
    Fixture to set up the database for each test function.
    It creates all tables before the test and drops them afterwards.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# --- Test Case ---
def test_prospect_lead_success(db_session: Session, mocker: MagicMock):
    """
    Tests the happy path for the /prospect/{lead_id} endpoint.
    - Mocks the FacebookService to return a valid page.
    - Verifies that the lead's status and details are updated correctly.
    """
    # 1. Arrange: Set up the initial data and mocks
    test_opp = Opportunity(
        title="Test Opportunity for Prospecting",
        agency="Test Agency",
        url="http://example.com/opp"
    )
    db_session.add(test_opp)
    db_session.commit()
    
    test_lead = Lead(
        opportunity_id=test_opp.id,
        business_name="Initial Placeholder",
        status="Identified"
    )
    db_session.add(test_lead)
    db_session.commit()
    
    # Mock the FacebookService methods called by the endpoint
    mocker.patch(
        "app.api.v1.endpoints.leads.FacebookService.find_page_by_name",
        return_value="12345"
    )
    mocker.patch(
        "app.api.v1.endpoints.leads.FacebookService.get_page_info",
        return_value={"name": "Mocked Facebook Page", "id": "12345"}
    )
    
    # 2. Act: Call the API endpoint
    response = client.post(f"/api/v1/leads/prospect/{test_lead.id}")
    
    # 3. Assert: Check the results
    assert response.status_code == 200, response.text
    
    response_data = response.json()
    assert response_data["message"] == "Lead successfully prospected."
    assert response_data["lead"]["status"] == "Prospected"
    assert response_data["lead"]["business_name"] == "Mocked Facebook Page"
    
    updated_lead = db_session.query(Lead).filter(Lead.id == test_lead.id).one()
    assert updated_lead.status == "Prospected"
    assert updated_lead.business_name == "Mocked Facebook Page"
    assert updated_lead.facebook_page_url == "https://www.facebook.com/12345" 