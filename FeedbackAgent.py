import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# Load environment variables from .env
load_dotenv()

class PersonaAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = Groq(api_key=self.api_key)
        self.embed_model = SentenceTransformer('all-MinLM-L6-v2')
    
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
            model="llama-3.1-70b-versatile",
            temperature=0.5 # Lower temperature for more consistent profiles
        )
        return completion.choices[0].message.content

    
    def create_embedding(self, user_data: dict):
        print("Processing persona for : ", {user_data.get('name')})

        persona_text = self._distill_persona(user_data)

        vector = self.embed_model.encode(persona_text).tolist()

        return {
            "id" : user_data.get("id"),
            "profile_summary": persona_text,
            "embedding": vector
        }

if __name__ == "__main__":
    print(" in main ")
    agent = PersonaAgent()
    
    sample_user = {
        "id": "user_01",
        "name": "Jordan",
        "age": 29,
        "hobbies": ["Urban exploration", "Synthesizer restoration"],
        "interests": ["Modular synths", "Industrial design", "Brativism"],
        "traits": "High openness, slightly cynical, extremely creative"
    }
    
    persona_packet = agent.create_embedding(sample_user)
    print("\nGenerated Profile Summary:")
    print(persona_packet["profile_summary"])
    print(f"\nVector Dimensions: {len(persona_packet['embedding'])}")