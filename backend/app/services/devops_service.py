import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any

class DevOpsService:
    """
    A service to interact with the Azure DevOps API.
    """
    def __init__(self):
        self.org_url = os.environ.get("ADO_ORG_URL")
        self.project_name = "GovBidGenie"
        self.pat = os.environ.get("ADO_PAT")

        if not self.org_url or not self.pat:
            raise ValueError("Azure DevOps credentials (ADO_ORG_URL, ADO_PAT) are not set in environment variables.")
        
        self.auth = HTTPBasicAuth('', self.pat)

        self.state_map = {
            "IDENTIFIED": "Identified",
            "PROSPECTED": "Prospected",
            "ENGAGED": "Engaged",
            "MESSAGED": "Messaged",
            "APPOINTMENT OFFERED": "Appointment Offered",
            "APPOINTMENT SET": "Appointment Set",
            "CONFIRMED": "Confirmed"
        }

    def _get_headers(self) -> Dict[str, str]:
        """Returns the headers for ADO."""
        return {'Content-Type': 'application/json-patch+json'}

    def _get_comment_headers(self) -> Dict[str, str]:
        """Returns the headers for adding a comment."""
        return {'Content-Type': 'application/json'}

    def create_work_item(self, lead_data: Dict[str, Any]) -> int:
        """
        Creates a new work item (Issue) in Azure DevOps.
        Returns the ID of the new work item.
        """
        url = f"{self.org_url}/{self.project_name}/_apis/wit/workitems/$Issue?api-version=7.1-preview.3"
        
        title = lead_data.get('business_name') or f"Lead from Opportunity {lead_data.get('opportunity_id')}"
        
        body = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": f"Initial lead created for opportunity ID: {lead_data.get('opportunity_id')}"},
            {"op": "add", "path": "/fields/System.State", "value": "To Do"},
        ]

        response = requests.post(url, json=body, headers=self._get_headers(), auth=self.auth)
        
        if not response.ok:
            print(f"ERROR: Failed to create work item. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()

        work_item = response.json()
        work_item_id = work_item['id']
        return work_item_id

    def update_work_item_status(self, work_item_id: int, new_status: str):
        """
        Updates the state of an existing work item in Azure DevOps.
        """
        devops_state = self.state_map.get(new_status.upper())
        if not devops_state:
            return

        url = f"{self.org_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.1-preview.3"
        
        body = [
            {"op": "add", "path": "/fields/System.State", "value": devops_state},
        ]

        response = requests.patch(url, json=body, headers=self._get_headers(), auth=self.auth)
        
        if not response.ok:
            print(f"ERROR: Failed to update work item. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()

    def add_comment_to_work_item(self, work_item_id: int, comment_text: str) -> Dict[str, Any]:
        """
        Adds a comment to an existing work item in Azure DevOps.

        Args:
            work_item_id: The ID of the work item.
            comment_text: The text of the comment to add.

        Returns:
            The JSON response from the API.
        """
        url = f"{self.org_url}/{self.project_name}/_apis/wit/workItems/{work_item_id}/comments?api-version=7.0-preview.3"
        
        body = {
            "text": comment_text
        }

        response = requests.post(url, json=body, headers=self._get_comment_headers(), auth=self.auth)
        
        if not response.ok:
            print(f"ERROR: Failed to add comment. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()
            
        return response.json()