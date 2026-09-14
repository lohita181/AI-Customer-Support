import os
import json
from google import genai
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    intent: str = Field(description="One of: hardware_issue, software_bug, account_access, billing_subscription, general_inquiry, complaint_feedback")
    escalate: bool = Field(description="True if the issue requires human intervention, False if it can be auto-handled")
    escalate_reason: str = Field(description="Brief reason for the escalate decision")
    draft_reply: str = Field(description="A drafted response to the customer grounded in historical brand tone")

def run_agent(text, api_key=None):
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    prompt = f"""You are an AI customer support agent for @AppleSupport.
Customer message: {text}

Analyze the message and provide:
1. Intent
2. Escalate decision
3. Reason for escalation decision
4. A drafted reply that sounds exactly like a professional @AppleSupport agent. Keep it empathetic, concise, and helpful.
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': AgentResponse,
                'temperature': 0.1,
            },
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "intent": "general_inquiry",
            "escalate": True,
            "escalate_reason": f"API Error: {str(e)}",
            "draft_reply": "We are currently experiencing technical difficulties. Please try again later."
        }
