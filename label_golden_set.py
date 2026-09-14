import os
import json
import pandas as pd
from google import genai
from pydantic import BaseModel, Field

class LabelResponse(BaseModel):
    intent: str = Field(description="One of: hardware_issue, software_bug, account_access, billing_subscription, general_inquiry, complaint_feedback")
    escalate: bool = Field(description="True if the issue requires human intervention or sensitive access, False if it can be auto-handled")
    escalate_reason: str = Field(description="Brief reason for the escalate decision")

def process_golden_set(input_csv, output_csv, sample_size=200):
    client = genai.Client()
    df = pd.read_csv(input_csv)
    df = df.head(sample_size).copy()
    
    intents = []
    escalates = []
    reasons = []
    
    for i, row in df.iterrows():
        customer_text = row['text_customer']
        prompt = f"Customer message: {customer_text}\nClassify the intent and decide if it needs human escalation."
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': LabelResponse,
                    'temperature': 0.0,
                },
            )
            data = json.loads(response.text)
            intents.append(data.get('intent', 'general_inquiry'))
            escalates.append(data.get('escalate', False))
            reasons.append(data.get('escalate_reason', ''))
        except Exception as e:
            intents.append("general_inquiry")
            escalates.append(True)
            reasons.append(f"Error parsing: {str(e)}")
            
    df['intent'] = intents
    df['escalate'] = escalates
    df['escalate_reason'] = reasons
    
    df.to_csv(output_csv, index=False)

if __name__ == '__main__':
    process_golden_set('processed_data.csv', 'golden_dataset.csv', sample_size=200)
