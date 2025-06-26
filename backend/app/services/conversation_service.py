import os
from app.db.models import Lead, ConversationLog

class ConversationService:
    def __init__(self):
        # In a real scenario, you would initialize your LLM client here
        # e.g., self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        pass

    def generate_initial_message(self, lead: Lead) -> str:
        """
        Generates the first message to send to a lead based on the opportunity.
        """
        opportunity_title = lead.opportunity.title
        business_name = lead.business_name

        prompt = f"We saw your work and thought you might be a great fit for an opportunity: '{opportunity_title}'. Are you open to discussing government contracts?"
        
        print(f"Generating initial message for {business_name} regarding '{opportunity_title}'")
        # In a real scenario, this prompt would be sent to an LLM
        # response = self.openai_client.completions.create(...)
        # mock_response = response.choices[0].text.strip()
        
        mock_response = f"Hi {business_name}, we're impressed with your work. We noticed a government contract for '{opportunity_title}' that seems like a perfect match for your company's skills. Is this something you'd be interested in exploring?"
        
        return mock_response

    def generate_response(self, conversation_history: list[ConversationLog]) -> str:
        """
        Generates a response based on the conversation history.
        """
        print("Generating a response based on conversation history...")
        # In a real scenario, you would format the history and send it to an LLM
        # formatted_history = "\n".join([f"{log.sender}: {log.message}" for log in conversation_history])
        # response = self.openai_client.completions.create(...)
        # mock_response = response.choices[0].text.strip()
        
        # Check for reschedule intent
        if "reschedule" in " ".join([log.message for log in conversation_history]):
             return "reschedule_intent_detected"

        mock_response = "That's great to hear! Would you be available for a brief 15-minute call next week to discuss the details?"
        
        return mock_response

    def analyze_conversation(self, conversation_history: list[ConversationLog]) -> dict:
        """
        Analyzes a completed conversation and returns a structured outcome.
        This is a placeholder for an LLM call.
        """
        print("--- Analyzing conversation for insights (mock) ---")
        
        full_transcript = "\n".join([f"{log.sender}: {log.message}" for log in conversation_history])
        
        # In a real scenario, an LLM would analyze the transcript.
        # Here, we'll just use some simple mock logic.
        outcome_tag = "unknown"
        summary = "No summary available."

        if "call next week" in full_transcript:
            outcome_tag = "successful_booking_offer"
            summary = "The AI successfully guided the conversation towards booking a meeting."
        elif "not interested" in full_transcript:
            outcome_tag = "not_interested"
            summary = "The lead explicitly stated they were not interested."
        
        print(f"Outcome determined: {outcome_tag}")

        return {
            "outcome_tag": outcome_tag,
            "summary": summary,
        }
