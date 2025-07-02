import os
import requests
from typing import Dict, Any, Optional
from app.db.models import Opportunity

class FacebookService:
    """
    Service to interact with the Facebook Graph API for managing a Page,
    including posting content and sending private replies to comments.
    """
    def __init__(self, page_id: Optional[str] = None, access_token: Optional[str] = None):
        self.page_id = page_id or os.environ.get("FACEBOOK_PAGE_ID")
        self.access_token = access_token or os.environ.get("FACEBOOK_ACCESS_TOKEN")
        if not self.page_id or not self.access_token:
            raise ValueError("Facebook credentials not provided. Set FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN or pass them to the constructor.")
        self.base_url = f"https://graph.facebook.com/v20.0/{self.page_id}"

    def send_private_reply(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        Sends a single private reply to a specific comment on a Page post.

        Args:
            comment_id: The ID of the comment to reply to.
            message: The text of the message to send.

        Returns:
            The JSON response from the Facebook API.
        """
        endpoint = f"https://graph.facebook.com/v20.0/{self.page_id}/messages"
        headers = {'Content-Type': 'application/json'}
        params = {'access_token': self.access_token}
        payload = {
            "recipient": {"comment_id": comment_id},
            "message": {"text": message},
            "messaging_type": "MESSAGE_TAG",
            "tag": "CONFIRMED_EVENT_UPDATE" # Or another appropriate tag
        }

        response = requests.post(endpoint, headers=headers, params=params, json=payload)
        
        if not response.ok:
            print(f"ERROR: Failed to send private reply. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()
            
        return response.json()

    def share_and_mention(self, message: str, link: str, target_page_id: str) -> Dict[str, Any]:
        """
        Shares a post to the Facebook Page's feed and mentions another page.

        Args:
            message: The text content of the post, which should include the mention.
                     The mention should be formatted as @[page_id].
            link: The URL of the post to share.
            target_page_id: The ID of the page to mention.

        Returns:
            The JSON response from the Facebook API, containing the new post's ID.
        """
        endpoint = f"{self.base_url}/feed"
        
        # Ensure the mention is correctly formatted in the message
        mention_tag = f"@[{target_page_id}]"
        if mention_tag not in message:
            # For simplicity, we'll append it if not present.
            # A more robust solution might ensure it's placed contextually.
            message = f"{message} {mention_tag}"

        params = {
            'message': message,
            'link': link,
            'access_token': self.access_token
        }

        response = requests.post(endpoint, params=params)

        if not response.ok:
            print(f"ERROR: Failed to share and mention. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()
            
        return response.json()

    def send_direct_message(self, recipient_page_id: str, message: str) -> Dict[str, Any]:
        """
        Sends a direct message to a Facebook Page's inbox.
        This is used for initiating contact, not replying to comments.
        """
        endpoint = f"https://graph.facebook.com/v20.0/me/messages"
        
        payload = {
            "recipient": {"id": recipient_page_id},
            "message": {"text": message},
            "messaging_type": "MESSAGE_TAG",
            "tag": "CONFIRMED_EVENT_UPDATE" # A generic tag for business communication
        }
        
        params = {'access_token': self.access_token}

        response = requests.post(endpoint, params=params, json=payload)
        
        if not response.ok:
            print(f"ERROR: Failed to send direct message. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()
            
        return response.json()

    def send_outreach_dm(self, recipient_id: str, commenter_name: str, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Sends a personalized outreach DM to a specific user (recipient).
        """
        endpoint = f"https://graph.facebook.com/v20.0/me/messages"
        
        message = (
            f"Hi {commenter_name}, thanks for your comment! "
            f"I saw that you're in the business of {opportunity.agency} and thought you might be "
            f"interested in a contract opportunity for '{opportunity.title}'. "
            f"You can see the details here: {opportunity.url}. "
            "Would you be open to a brief chat about it?"
        )
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": "MESSAGE_TAG",
            "tag": "CONFIRMED_EVENT_UPDATE"
        }
        
        params = {'access_token': self.access_token}

        response = requests.post(endpoint, params=params, json=payload)
        
        if not response.ok:
            print(f"ERROR: Failed to send DM. Status: {response.status_code}, Body: {response.text}")
            response.raise_for_status()
            
        return response.json()

    def get_page_info(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches basic public information for a given Page ID.
        """
        endpoint = f"https://graph.facebook.com/v20.0/{page_id}"
        params = {
            'fields': 'id,name,category',
            'access_token': self.access_token
        }

        response = requests.get(endpoint, params=params)

        if not response.ok:
            print(f"ERROR: Failed to get page info for ID '{page_id}'. Status: {response.status_code}, Body: {response.text}")
            return None
        
        return response.json()

    def find_page_by_name(self, page_name: str) -> Optional[str]:
        """
        Searches for a Facebook Page by its name and returns the ID of the top result.

        Args:
            page_name: The name of the page to search for.

        Returns:
            The Page ID as a string if a page is found, otherwise None.
        """
        endpoint = "https://graph.facebook.com/v20.0/pages/search"
        params = {
            'q': page_name,
            'fields': 'id,name',
            'limit': 1, # We only want the most likely result
            'access_token': self.access_token
        }

        response = requests.get(endpoint, params=params)

        if not response.ok:
            print(f"ERROR: Failed to search for page '{page_name}'. Status: {response.status_code}, Body: {response.text}")
            return None
        
        data = response.json().get('data', [])
        if data:
            top_result = data[0]
            print(f"Found page '{top_result['name']}' with ID {top_result['id']} for search term '{page_name}'")
            return top_result['id']
        else:
            print(f"No Facebook Page found for search term '{page_name}'")
            return None
