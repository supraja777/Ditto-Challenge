import os
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

class PersonaAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = Groq(api_key=self.api_key)
        # FIX: Changed 'all-MinLM-L6-v2' to 'all-MiniLM-L6-v2' (added the 'i')
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def _distill_persona(self, user_data: dict) -> str:
        prompt = (
            f"Analyze the following user data and write a dense, one-paragraph "
            f"psychological and lifestyle profile. Focus on their 'vibe', "
            f"social energy, and core values. Data: {user_data}"
        )

        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert psychologist and profiler."},
                {"role": "user", "content": prompt}
            ],
            # FIX: Using the currently supported Llama 3.3 model
            model="llama-3.3-70b-versatile",
            temperature=0.5 
        )
        return completion.choices[0].message.content

    def create_embedding(self, user_data: dict):
        print(f"Processing persona for: {user_data.get('name')}")
        persona_text = self._distill_persona(user_data)
        vector = self.embed_model.encode(persona_text).tolist()

        return {
            "id": user_data.get("id"),
            "profile_summary": persona_text,
            "embedding": vector
        }

# --- New Agent: MatchmakingAgent ---

class MatchmakingAgent:
    def __init__(self):
        self.user_pool = []

    def add_to_pool(self, persona_packet):
        self.user_pool.append(persona_packet)

    def find_match(self, target_id):
        target = next((u for u in self.user_pool if u['id'] == target_id), None)
        if not target: return "User not found."

        # Convert to numpy for similarity calculation
        target_vec = np.array(target['embedding']).reshape(1, -1)
        
        best_score = -1
        best_match = None

        for user in self.user_pool:
            if user['id'] == target_id: continue
            
            candidate_vec = np.array(user['embedding']).reshape(1, -1)
            # Calculate Cosine Similarity
            score = cosine_similarity(target_vec, candidate_vec)[0][0]
            
            if score > best_score:
                best_score = score
                best_match = user

        return best_match, best_score

if __name__ == "__main__":
    agent = PersonaAgent()
    matcher = MatchmakingAgent()
    
    # Create two users to test matching
    user_a = {
        "id": "user_01", "name": "Jordan", "age": 29, 
        "hobbies": ["Synthesizer restoration"], "traits": "Creative, analytical"
    }
    user_b = {
        "id": "user_02", "name": "Casey", "age": 31, 
        "hobbies": ["Vinyl collecting", "Music production"], "traits": "Artistic, focused"
    }
    
    packet_a = agent.create_embedding(user_a)
    packet_b = agent.create_embedding(user_b)
    
    matcher.add_to_pool(packet_a)
    matcher.add_to_pool(packet_b)
    
    match, score = matcher.find_match("user_01")
    print(f"\nMatch Found: {match['id']} with a Compatibility Score of: {score:.4f}")