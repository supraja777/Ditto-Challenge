import os
from groq import Groq
import json

import os
from dotenv import load_dotenv
load_dotenv()

from app_logging import setup_matchmaking_loggers
system_log, ai_log = setup_matchmaking_loggers()

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
def get_agent_response(self_info, partner_name, history):
    """Generates a response for a specific user persona."""
    
    system_prompt = f"""
    You are {self_info['user_name']}. 
    Personality: {self_info['personality']}
    Social Energy (1-10): {self_info['social_energy']}
    Intellectual Focus: {self_info['intellectual_focus']}
    Traits: {', '.join(self_info['traits'])}
    
    Goal: Have a natural first-date conversation with {partner_name}. 
    STRICT RULE: Stay in character. If your social energy is low, be brief. 
    If it's high, be more engaging. Speak only as yourself.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile", # High reasoning for persona depth
        temperature=0.7,
    )
    return chat_completion.choices[0].message.content

def judge_verdict(user_a, user_b, transcript):
    """The Judge Agent evaluates the conversation for compatibility and volume."""
    
    judge_prompt = f"""
    You are a Matchmaking Judge. Review the transcript between {user_a['user_name']} and {user_b['user_name']}.
    
    User A Deal Breakers: {user_a['deal_breakers']}
    User B Deal Breakers: {user_b['deal_breakers']}
    
    CRITERIA:
    1. DEAL BREAKERS: If either user triggered a deal breaker, confidence_score = 0.
    2. SYNERGY: Did they connect on their Intellectual Focus or Hobbies?
    3. VOLUME BIAS: Your goal is to maximize matches. If there is no conflict, be optimistic.
    
    OUTPUT JSON ONLY:
    {{
        "confidence_score": float (0-1),
        "reasoning": "string explaining the verdict",
        "is_match": boolean
    }}
    """
    
    messages = [
        {"role": "system", "content": judge_prompt},
        {"role": "user", "content": f"Transcript: {json.dumps(transcript)}"}
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.1-8b-instant", # Faster for judging
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def date_simulation(user_a, user_b, rounds=1):
    """The main entry point for simulating a pair."""
    print(f"--- Simulating: {user_a['user_name']} x {user_b['user_name']} ---")
    
    transcript = []
    
    for _ in range(rounds):
        # User A speaks
        resp_a = get_agent_response(user_a, user_b['user_name'], transcript)
        transcript.append({"role": "user", "name": user_a['user_name'], "content": resp_a})
        print(f"{user_a['user_name']}: {resp_a}")
        
        # User B speaks
        resp_b = get_agent_response(user_b, user_a['user_name'], transcript)
        transcript.append({"role": "user", "name": user_b['user_name'], "content": resp_b})
        print(f"{user_b['user_name']}: {resp_b}")

    verdict = judge_verdict(user_a, user_b, transcript)
    system_log.info(f"END_SIMULATION: {user_a['user_name']} vs {user_b['user_name']} - SUCCESS")
    print("What is the verdict ? ", verdict)
    return verdict["confidence_score"]