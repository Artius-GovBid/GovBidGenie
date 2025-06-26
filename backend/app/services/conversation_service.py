import os
from openai import OpenAI
import json
from typing import List, Dict, Any
from app.db.models import Lead, ConversationLog
from openai.types.chat import ChatCompletionMessageParam

class ConversationService:
    def __init__(self):
        # It's good practice to load the API key from environment variables
        # for security and flexibility.
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_initial_message(self, lead: Dict[str, Any]) -> str:
        """
        Generates an initial message to a lead based on the opportunity details.
        """
        opportunity_title = lead.get('opportunity_title', 'N/A')
        opportunity_description = lead.get('opportunity_description', 'N/A')
        agency_name = lead.get('agency_name', 'N/A')

        prompt = f"""
        You are an expert government contract acquisition specialist. Your task is to craft a compelling, concise, and professional initial outreach message to a potential government lead on Facebook.

        **Opportunity Details:**
        - **Title:** {opportunity_title}
        - **Agency:** {agency_name}
        - **Description:** {opportunity_description}

        **Instructions:**
        1.  Start with a polite and professional greeting.
        2.  Reference the specific government agency ({agency_name}) to show you've done your research.
        3.  Briefly mention your company's expertise related to the opportunity.
        4.  Keep the message under 80 words.
        5.  End with a clear call to action, such as asking if they are the right person to speak with or suggesting a brief chat.
        6.  Do not use emojis or overly casual language.

        Draft the message below.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            message_content = response.choices[0].message.content
            return message_content.strip() if message_content else "Could not generate a message."
        except Exception as e:
            print(f"Error generating initial message: {e}")
            return "Hello, we are a company that specializes in government contracts and we believe we can help you. Would you be open to a brief chat?"

    def generate_response(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generates a follow-up response based on the conversation history.
        """
        prompt = """
        You are an expert government contract acquisition specialist continuing a conversation on Facebook. Your goal is to be helpful, build rapport, and guide the conversation towards booking a meeting.

        Below is the conversation history. The last message is from the potential lead. Your task is to draft the next response from our side.

        **Instructions:**
        1.  Analyze the tone and intent of the lead's last message.
        2.  Address their questions or comments directly and professionally.
        3.  If they show interest, suggest scheduling a brief call and provide a hypothetical link (e.g., "calendly.com/our-team").
        4.  If they seem hesitant or have objections, address their concerns concisely and offer more information.
        5.  Keep the response professional, friendly, and concise (under 80 words).
        6.  Do not use emojis.

        **Conversation History:**
        """

        messages_for_api: List[ChatCompletionMessageParam] = [{"role": "system", "content": prompt}]
        for message in conversation_history:
            role = "assistant" if message['sender'] == 'bot' else "user"
            messages_for_api.append({"role": role, "content": message['text']}) # type: ignore

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages_for_api,
                temperature=0.7,
                max_tokens=150,
            )
            message_content = response.choices[0].message.content
            return message_content.strip() if message_content else "Could not generate a response."
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Thank you for your response. Would you be available for a quick call next week to discuss this further?"

    def analyze_conversation(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyzes the conversation to determine the outcome and summarize it.
        """
        prompt = f"""
        You are an AI assistant tasked with analyzing a conversation for a government contracting business.
        Based on the conversation history provided below, please determine the outcome and provide a brief summary.

        **Conversation History:**
        {json.dumps(conversation_history, indent=2)}

        **Instructions:**
        Respond with a JSON object with two keys:
        1.  `tag`: A single-word tag for the conversation outcome. Choose from: `APPOINTMENT_SET`, `NOT_INTERESTED`, `FOLLOW_UP_LATER`, `WRONG_PERSON`, `NEEDS_MORE_INFO`, `GHOSTED`, `ESCALATED`.
        2.  `summary`: A one-sentence summary of the conversation and its outcome.

        **Example Response:**
        {{
          "tag": "APPOINTMENT_SET",
          "summary": "The lead expressed interest and agreed to a meeting, which has been scheduled."
        }}

        Provide only the JSON object in your response.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that provides JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            message_content = response.choices[0].message.content
            if not message_content:
                raise ValueError("No content in response")
            analysis = json.loads(message_content)
            return {
                "tag": analysis.get("tag", "NEEDS_MORE_INFO"),
                "summary": analysis.get("summary", "Analysis failed.")
            }
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            return {
                "tag": "ANALYSIS_FAILED",
                "summary": "An error occurred during conversation analysis."
            }

# Example Usage (for testing)
if __name__ == '__main__':
    # Make sure to set the OPENAI_API_KEY environment variable before running
    # For example: export OPENAI_API_KEY='your_key_here'
    
    # You might need to add the project root to PYTHONPATH to run this directly
    # export PYTHONPATH=$PYTHONPATH:$(pwd)
    
    service = ConversationService()

    # Test 1: Generate Initial Message
    print("--- Testing Initial Message Generation ---")
    mock_lead = {
        "opportunity_title": "Cybersecurity Infrastructure Upgrade",
        "opportunity_description": "Seeking a vendor to overhaul our agency's cybersecurity infrastructure, including firewall, IDS/IPS, and endpoint protection.",
        "agency_name": "Department of Defense"
    }
    initial_message = service.generate_initial_message(mock_lead)
    print("Generated Message:")
    print(initial_message)
    print("\\n" + "="*50 + "\\n")

    # Test 2: Generate a Response
    print("--- Testing Response Generation ---")
    mock_history = [
        {"sender": "bot", "text": "Hello, I'm reaching out from a firm specializing in cybersecurity for government agencies. We noted the Department of Defense's recent call for a cybersecurity infrastructure overhaul. Are you the appropriate person to discuss this opportunity?"},
        {"sender": "lead", "text": "Yes, I am. What makes you think you can handle a project of this scale?"}
    ]
    response_message = service.generate_response(mock_history)
    print("Generated Response:")
    print(response_message)
    print("\\n" + "="*50 + "\\n")

    # Test 3: Analyze a Conversation
    print("--- Testing Conversation Analysis ---")
    mock_history_for_analysis = [
        {"sender": "bot", "text": "Hello, I'm reaching out from a firm specializing in cybersecurity for government agencies. We noted the Department of Defense's recent call for a cybersecurity infrastructure overhaul. Are you the appropriate person to discuss this opportunity?"},
        {"sender": "lead", "text": "Yes, I am. What makes you think you can handle a project of this scale?"},
        {"sender": "bot", "text": "We have over a decade of experience and have successfully completed similar projects for other federal agencies. We can provide case studies and references. Would you be open to a 15-minute call next week to discuss our qualifications further? You can book a time here: calendly.com/our-team"},
        {"sender": "lead", "text": "That sounds good. I've just booked a slot for Tuesday at 10 AM."}
    ]
    analysis = service.analyze_conversation(mock_history_for_analysis)
    print("Conversation Analysis:")
    print(json.dumps(analysis, indent=2))
    print("\\n" + "="*50 + "\\n")
