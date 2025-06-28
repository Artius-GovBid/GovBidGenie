import os
import requests
import time
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from a .env file if it exists
load_dotenv() 

BASE_URL = "http://127.0.0.1:8000"

def check_server_health():
    """Checks if the FastAPI server is running."""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("--- FastAPI server is running. ---")
            return True
        else:
            print(f"--- Server returned status {response.status_code}. ---")
            return False
    except requests.ConnectionError:
        print("--- FastAPI server is not running. ---")
        return False

def run_test():
    """Runs the end-to-end test."""
    print("--- Starting End-to-End Test ---")

    # 1. Define a mock opportunity from SAM.gov
    mock_opportunity = {
        "sam_gov_id": f"test-opp-{int(time.time())}",
        "title": "Test Opportunity for E2E",
        "url": "http://sam.gov/opp/test-opp",
        "agency": "Test Agency",
        "posted_date": "2024-01-01T12:00:00Z"
    }

    print(f"--- Step 1: Creating lead for opportunity: {mock_opportunity['sam_gov_id']} ---")

    # 2. Call the create_lead endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/v1/leads", json=mock_opportunity)
        response.raise_for_status() # Raise an exception for bad status codes
        
        response_data = response.json()
        print(f"--- API Response: {response_data} ---")
        
        lead_id = response_data.get("lead_id")
        ado_work_item_id = response_data.get("azure_devops_work_item_id")

        if lead_id and ado_work_item_id:
            print(f"--- SUCCESS: Lead created (ID: {lead_id}) and ADO work item created (ID: {ado_work_item_id}). ---")
        elif lead_id:
            print(f"--- WARNING: Lead created (ID: {lead_id}) but ADO work item creation failed. ---")
        else:
            print(f"--- FAILURE: Could not create lead. ---")

    except requests.exceptions.RequestException as e:
        print(f"--- FAILURE: API request failed: {e} ---")
        if e.response:
            print(f"--- Response Body: {e.response.text} ---")

if __name__ == "__main__":
    if not check_server_health():
        print("\nPrerequisites failed. Please ensure the FastAPI server is running before executing the test.")
    else:
        run_test()
