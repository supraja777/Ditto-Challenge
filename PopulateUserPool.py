from PersonaAgent import PersonaAgent
from MatchMakingAgent import MatchmakingAgent
def get_sample_users():
    """Returns a list of 10 diverse user dictionaries."""
    return [
        {"id": "U01", "name": "Jordan", "age": 25, "hobbies": ["Digital Art", "Indie Games"], "interests": ["Cyberpunk", "UI Design"], "traits": "Introverted, Creative"},
        {"id": "U02", "name": "Casey", "age": 28, "hobbies": ["Marathon Running", "Meal Prep"], "interests": ["Nutrition", "Biohacking"], "traits": "High-Energy, Disciplined"},
        {"id": "U03", "name": "Alex", "age": 34, "hobbies": ["Antique Restoration", "Jazz"], "interests": ["History", "Vinyl"], "traits": "Patient, Sophisticated"},
        {"id": "U04", "name": "Sam", "age": 22, "hobbies": ["Skating", "Graffiti Art"], "interests": ["Streetwear", "Hip Hop"], "traits": "Extroverted, Rebellious"},
        {"id": "U05", "name": "Taylor", "age": 30, "hobbies": ["Gardening", "Baking"], "interests": ["Sustainability", "Cottagecore"], "traits": "Nurturing, Calm"},
        {"id": "U06", "name": "Morgan", "age": 27, "hobbies": ["Chess", "Stock Trading"], "interests": ["Economics", "Strategy"], "traits": "Analytical, Competitive"},
        {"id": "U07", "name": "Riley", "age": 31, "hobbies": ["Scuba Diving", "Photography"], "interests": ["Marine Biology", "Travel"], "traits": "Adventurous, Observant"},
        {"id": "U08", "name": "Jamie", "age": 26, "hobbies": ["Cosplay", "Anime"], "interests": ["Japanese Culture", "Sewing"], "traits": "Passionate, Quirky"},
        {"id": "U09", "name": "Skyler", "age": 35, "hobbies": ["Mountain Biking", "Camping"], "interests": ["Geology", "Outdoor Survival"], "traits": "Rugged, Independent"},
        {"id": "U10", "name": "Charlie", "age": 29, "hobbies": ["Stand-up Comedy", "Podcasting"], "interests": ["Pop Culture", "Social Media"], "traits": "Funny, Talkative"}
    ]

def populate_system(persona_agent, matchmaking_agent):
    """Processes users through embeddings and adds them to the Matchmaking pool."""
    users = get_sample_users()
    print(f"--- Starting Population of {len(users)} Users ---")
    
    for user_data in users:
        # 1. Generate Persona Packet (LLM Distillation + Vector)
        try:
            persona_packet = persona_agent.create_embedding(user_data)
            
            # 2. Add raw data back into packet (MatchmakingAgent needs Age/Traits for heuristics)
            persona_packet.update({
                "name": user_data["name"],
                "age": user_data["age"],
                "traits": user_data["traits"]
            })
            
            # 3. Add to Matchmaking pool
            matchmaking_agent.add_to_pool(persona_packet)
            print(f"✅ Successfully added {user_data['name']}")
        except Exception as e:
            print(f"❌ Failed to add {user_data['name']}: {e}")

    print("--- Population Complete ---\n")

# # --- Execution Logic (If run standalone) ---
# if __name__ == "__main__":

#     p_agent = PersonaAgent()
#     m_agent = MatchmakingAgent()
    
#     populate_system(p_agent, m_agent)
    
#     # Test: Find Top 5 for Jordan (U01)
#     results = m_agent.get_top_matches("U01", top_k=5)
    
#     print(f"TOP 5 MATCHES FOR JORDAN:")
#     for i, res in enumerate(results):
#         print(f"{i+1}. {res['name']} (Score: {res['final_score']}) - Vibe: {res['metrics']['vibe_similarity']}")