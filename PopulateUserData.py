import json
import os
from database.User import User
from agents.PersonaAgent import PersonaAgent

class PopulateUserData:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.user_db = User()
        self.persona_agent = PersonaAgent()

    def flatten_vector(self, vec):
        if vec is None: return None
        # If it's a list of lists, take the first element
        if isinstance(vec, list) and len(vec) > 0 and isinstance(vec[0], list):
            return vec[0]
        return vec
    
    def clean_list(self, val):
        if isinstance(val, str):
            return [item.strip() for item in val.split(',') if item.strip()]
        return val if isinstance(val, list) else []

    def start_migration(self):
        if not os.path.exists(self.json_file_path):
            print(f"❌ Error: File {self.json_file_path} not found.")
            return

        try:
            with open(self.json_file_path, 'r') as f:
                users_data = json.load(f)

            print(f"🚀 Starting AI-Enhanced migration for {len(users_data)} users...")

            success_count = 0
            for index, user_entry in enumerate(users_data):
              
                # 1. Prepare raw data for the Agent
                # We send the whole entry so the LLM has context
                persona_results = self.persona_agent.create_embedding(user_entry)
                traits = self.clean_list(user_entry.get("traits"))
                hobbies = self.clean_list(user_entry.get("hobbies"))
                dealbreakers = self.clean_list(user_entry.get("dealbreakers"))

                # 3. Combine original data with AI-generated data
                data_object = {
                    # --- CORE IDENTITY ---
                    "name": user_entry.get("name"),
                    "age": user_entry.get("age"),
                    "traits": traits,
                    
                    # --- AI GENERATED (From PersonaAgent) ---
                    "profile_summary": persona_results.get("profile_summary"), 
                    "embedding": self.flatten_vector(persona_results.get("embedding")), 
                    "trait_embedding":self.flatten_vector(persona_results.get("trait_embeddings")),         
                    
                    # --- RICH COMPUTATION FACTORS ---
                    "social_energy": int(user_entry.get("social_energy", 5)),
                    "intent": user_entry.get("intent", "Exploring"),
                    "intellectual_focus": user_entry.get("intellectual_focus", "General"),
                    "dealbreakers": dealbreakers,
                    "hobbies": hobbies
                }

                print(f"🚀 Starting AI-Enhanced migration for {data_object['name']}...")

                print("Data object being uploaded is - ", data_object)

                # 4. Upload to Supabase
                user_id = self.user_db.add_user(data_object)
                
                if user_id:
                    success_count += 1
                    print(f"✅ [{index+1}] Fully Migrated: {data_object['name']}")
                else:
                    print(f"❌ [{index+1}] Failed: {data_object['name']}")

            print(f"\n✨ Migration Complete! {success_count} users are now live with AI embeddings.")

        except Exception as e:
            print(f"❌ Migration interrupted: {e}")

if __name__ == "__main__":
    JSON_PATH = "UserPool.json" 
    populator = PopulateUserData(JSON_PATH)
    populator.start_migration()