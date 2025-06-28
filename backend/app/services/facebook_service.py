import os
import requests
from typing import Dict, Any, Optional

class FacebookService:
    """
    Service to interact with the Facebook Graph API for managing a Page,
    including posting content and sending private replies to comments.
    """
    def __init__(self):
        self.page_id = os.environ.get("FACEBOOK_PAGE_ID")
        self.access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
        if not self.page_id or not self.access_token:
            raise ValueError("FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN environment variables must be set.")
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
