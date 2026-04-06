import os
from groq import Groq
from agents.MatchMakingAgent import MatchmakingAgent
from agents.PersonaAgent import PersonaAgent

class DateSimulationAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.chat_model = "llama-3.1-8b-instant"  # Fast for conversation
        self.eval_model = "llama-3.3-70b-versatile" # Smart for scoring

    def _generate_persona_response(self, user_profile, conversation_history, partner_name):
        """Simulates one turn of a specific user persona."""
        system_prompt = (
            f"You are {user_profile['name']}. Your personality: {user_profile['profile_summary']}. "
            f"You are on a first date with {partner_name}. "
            "Stay in character. Be natural, don't be an AI. Give short-to-medium responses."
        )
        
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history
            ],
            model=self.chat_model,
            max_tokens=150
        )
        return completion.choices[0].message.content

    def simulate_date(self, user_a, user_b, turns=3):
        """Runs a back-and-forth dialogue between two personas."""
        print(f"--- Simulating Date: {user_a['name']} & {user_b['name']} ---")
        history = []
        transcript = ""

        for i in range(turns):
            # User A speaks
            resp_a = self._generate_persona_response(user_a, history, user_b['name'])
            history.append({"role": "user", "content": f"{user_a['name']}: {resp_a}"})
            transcript += f"{user_a['name']}: {resp_a}\n\n"

            # User B speaks
            resp_b = self._generate_persona_response(user_b, history, user_a['name'])
            history.append({"role": "user", "content": f"{user_b['name']}: {resp_b}"})
            transcript += f"{user_b['name']}: {resp_b}\n\n"

        # Evaluate the transcript
        evaluation = self._evaluate_transcript(transcript, user_a['name'], user_b['name'])
        return {
            "match_id": user_b['id'],
            "transcript": transcript,
            "impression_score": evaluation['score'],
            "critique": evaluation['critique']
        }

    def _evaluate_transcript(self, transcript, name_a, name_b):
        """Uses a high-reasoning model to judge the 'vibe' of the conversation."""
        eval_prompt = (
            f"Analyze this date transcript between {name_a} and {name_b}:\n\n{transcript}\n\n"
            "On a scale of 0-100, how much 'chemistry' or 'conversational flow' was there? "
            "Identify friction points. Return ONLY a JSON object: "
            "{'score': int, 'critique': 'string'}"
        )
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": eval_prompt}],
            model=self.eval_model,
            response_format={"type": "json_object"}
        )
        import json
        return json.loads(response.choices[0].message.content)

# # --- Orchestrating the Top 5 Simulation ---
# # 1. Initialize the agents (The Instances)
# p_agent = PersonaAgent()
# m_agent = MatchmakingAgent() # Create the instance 'm_agent'

# # 2. Populate the pool (Using your populateUserPool script)
# from PopulateUserPool import populate_system
# populate_system(p_agent, m_agent)

# # 3. Call the method on the INSTANCE (m_agent), not the CLASS (MatchmakingAgent)
# top_5 = m_agent.get_top_matches("U01") # 'target_id' is "U01"

# # 4. Now run the simulation
# # --- Setup ---
# sim_agent = DateSimulationAgent()
# user_a_profile = next(u for u in m_agent.user_pool if u['id'] == "U01")

# # Variables to track the "Ultimate Match"
# best_sim_score = -1
# ultimate_match_profile = None
# winning_result_packet = None

# print(f"\n🚀 Starting Simulations for {user_a_profile['name']}...\n")

# # --- The Loop ---
# for match in top_5:
#     # 1. Get the full profile from the pool
#     user_b_profile = next(u for u in m_agent.user_pool if u['id'] == match['id'])
    
#     # 2. Run the Date Simulation
#     result = sim_agent.simulate_date(user_a_profile, user_b_profile)
#     current_score = result['impression_score']
    
#     print(f"✔️ Finished Date with {match['name']} | Sim Score: {current_score}/100")

#     # 3. "The Selection Logic": Keep track of the highest score
#     if current_score > best_sim_score:
#         best_sim_score = current_score
#         ultimate_match_profile = user_b_profile
#         winning_result_packet = result

# # --- The Presentation ---
# print("\n" + "="*50)
# print("🏆 ULTIMATE MATCH FOUND 🏆")
# print("="*50)
# print(f"Partner: {ultimate_match_profile['name']} (ID: {ultimate_match_profile['id']})")
# print(f"Final Chemistry Score: {best_sim_score}/100")
# print(f"\nAgent Critique:\n{winning_result_packet['critique']}")
# print("-" * 50)
# print(f"Sample Interaction:\n{winning_result_packet['transcript'][:300]}...")
# print("="*50)