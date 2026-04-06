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
