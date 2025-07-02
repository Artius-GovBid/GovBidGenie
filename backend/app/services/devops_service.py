import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any
from app.db.models import Lead, Opportunity
from sqlalchemy.orm import Session

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
            "CONFIRMED": "Confirmed",
            "DONE": "Done"
        }

    def _get_headers(self) -> Dict[str, str]:
        """Returns the headers for ADO."""
        return {'Content-Type': 'application/json-patch+json'}

    def _get_comment_headers(self) -> Dict[str, str]:
        """Returns the headers for adding a comment."""
        return {'Content-Type': 'application/json'}

    def create_work_item(self, title: str, opportunity_url: str, agency: str, source: str) -> Any:
        """
        Creates a new work item (Issue) in Azure DevOps.
        Returns the created work item object.
        """
        url = f"{self.org_url}/{self.project_name}/_apis/wit/workitems/$Issue?api-version=7.1-preview.3"
        
        description = (
            f"<b>Source:</b> {source}<br>"
            f"<b>Agency:</b> {agency}<br>"
            f"<b>Opportunity Link:</b> <a href='{opportunity_url}'>{opportunity_url}</a>"
        )

        body = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/System.State", "value": "Identified"},
        ]

        response = requests.post(url, json=body, headers=self._get_headers(), auth=self.auth)
        
        if not response.ok:
            print(f"ERROR: Failed to create work item. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()

        return response.json()

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

    def create_work_item_from_lead(self, lead: Lead, db: Session):
        """
        Creates an Azure DevOps work item from a Lead object and updates the lead.
        """
        # Ensure the lead's opportunity is loaded
        if not lead.opportunity:
            lead = db.query(Lead).filter(Lead.id == lead.id).one()

        title = f"New Lead: {lead.opportunity.title}"
        
        # Explicitly get the string value from the model attributes
        opportunity_url = getattr(lead.opportunity, 'url', '') or ''
        agency = getattr(lead.opportunity, 'agency', 'N/A') or 'N/A'
        source = getattr(lead, 'source', 'Facebook') or 'Facebook'

        new_ado_item = self.create_work_item(
            title=title,
            opportunity_url=opportunity_url,
            agency=agency,
            source=source
        )
        
        new_ado_id = new_ado_item.get("id")
        if new_ado_id:
            lead.azure_devops_work_item_id = new_ado_id
            db.commit()
            print(f"Updated lead {lead.id} with ADO work item ID {new_ado_id}")

        return new_ado_item