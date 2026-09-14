import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from baselines import run_trivial_baseline, run_simple_baseline
from agent import run_agent
from google import genai
from pydantic import BaseModel, Field

class JudgeResponse(BaseModel):
    score: int = Field(description="Score from 1 to 5")
    reasoning: str = Field(description="Reasoning for the score")

def run_evaluation(golden_csv):
    df = pd.read_csv(golden_csv)
    
    true_intents = df['intent'].tolist()
    true_escalates = df['escalate'].tolist()
    
    trivial_intents = []
    trivial_escalates = []
    
    simple_intents = []
    simple_escalates = []
    
    agent_intents = []
    agent_escalates = []
    agent_replies = []
    
    for i, row in df.iterrows():
        text = row['text_customer']
        
        t_res = run_trivial_baseline(text)
        trivial_intents.append(t_res['intent'])
        trivial_escalates.append(t_res['escalate'])
        
        s_res = run_simple_baseline(text)
        simple_intents.append(s_res['intent'])
        simple_escalates.append(s_res['escalate'])
        
        a_res = run_agent(text)
        agent_intents.append(a_res['intent'])
        agent_escalates.append(a_res['escalate'])
        agent_replies.append(a_res['draft_reply'])
        
    print("--- Intent Classification Accuracy ---")
    print(f"Trivial: {accuracy_score(true_intents, trivial_intents):.4f}")
    print(f"Simple:  {accuracy_score(true_intents, simple_intents):.4f}")
    print(f"Agent:   {accuracy_score(true_intents, agent_intents):.4f}")
    
    print("\n--- Escalation F1 Score ---")
    print(f"Trivial: {f1_score(true_escalates, trivial_escalates, zero_division=0):.4f}")
    print(f"Simple:  {f1_score(true_escalates, simple_escalates, zero_division=0):.4f}")
    print(f"Agent:   {f1_score(true_escalates, agent_escalates, zero_division=0):.4f}")
    
    print("\n--- Running LLM-as-a-Judge on Agent Replies ---")
    client = genai.Client()
    scores = []
    
    for i, row in df.iterrows():
        text = row['text_customer']
        draft = agent_replies[i]
        
        prompt = f"""You are an expert customer service evaluator.
Customer: {text}
Agent Draft: {draft}

Grade the Agent Draft from 1 to 5 based on empathy, brand tone, and helpfulness.
"""
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': JudgeResponse,
                    'temperature': 0.0,
                }
            )
            data = json.loads(response.text)
            scores.append(data.get('score', 3))
        except:
            scores.append(3)
            
    avg_score = sum(scores) / len(scores)
    print(f"Average Agent Reply Score (out of 5): {avg_score:.2f}")

if __name__ == '__main__':
    run_evaluation('golden_dataset.csv')
