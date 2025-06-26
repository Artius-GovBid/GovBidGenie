import os
from datetime import datetime, timedelta

class CalendarService:
    def __init__(self):
        # In a real scenario, you'd initialize the MSAL client for OAuth
        # and get an access token for the Microsoft Graph API.
        pass

    def get_availability(self) -> list[dict]:
        """
        Fetches available 15-minute appointment slots for the next 7 days.
        This is a placeholder implementation.
        """
        print("--- Fetching available appointment slots (mock) ---")
        
        available_slots = []
        now = datetime.utcnow()
        
        # Generate some mock slots for the next 3 business days between 9am and 5pm UTC
        for day in range(1, 4):
            for hour in range(9, 17):
                for minute in [0, 15, 30, 45]:
                    slot_time = (now + timedelta(days=day)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                    available_slots.append({
                        "start_time": slot_time.isoformat() + "Z",
                        "end_time": (slot_time + timedelta(minutes=15)).isoformat() + "Z"
                    })
        
        print(f"Found {len(available_slots)} available slots.")
        return available_slots

    def create_appointment(self, start_time: str, end_time: str, title: str, lead_email: str) -> dict:
        """
        Creates a new appointment in the calendar.
        This is a placeholder implementation.
        """
        print(f"--- Creating appointment (mock) ---")
        print(f"Title: {title}")
        print(f"Time: {start_time} to {end_time}")
        print(f"Inviting: {lead_email}")
        
        # In a real implementation, you would use the Microsoft Graph API
        # to create an event and would get back a unique event ID.
        mock_event_id = f"mock_event_{int(datetime.now().timestamp())}"
        
        print(f"Successfully created mock appointment with ID: {mock_event_id}")
        return {"event_id": mock_event_id, "status": "tentative"}
