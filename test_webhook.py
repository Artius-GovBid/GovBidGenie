import requests
import json

def send_test_webhook():
    """
    Sends a simulated Facebook webhook event to the local server.
    """
    url = "http://127.0.0.1:8000/api/v1/webhooks/facebook"
    
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "12345",
                "time": 1722883200,
                "changes": [
                    {
                        "field": "feed",
                        "value": {
                            "item": "comment",
                            "verb": "add",
                            "comment_id": "67890",
                            "from": {
                                "id": "54321",
                                "name": "Test User"
                            },
                            "message": "I am looking for janitorial services contracts.",
                            "post_id": "12345_67890"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        print("Webhook sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to send webhook: {e}")

if __name__ == "__main__":
    send_test_webhook() 