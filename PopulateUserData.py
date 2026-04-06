import json
import os
from database.User import User
from PersonaAgent import PersonaAgent

class PopulateUserData:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.user_db = User()
        self.persona_agent = PersonaAgent()

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
                print(f"🚀 Starting AI-Enhanced migration for {data_object['name']}...")
                # 1. Prepare raw data for the Agent
                # We send the whole entry so the LLM has context
                ai_results = self.persona_agent.create_embedding(user_entry)

                # 2. Clean up traits (string -> list)
                traits = user_entry.get("traits", []) # Note: your JSON used 'traits', table uses 'current_traits'
                if isinstance(traits, str):
                    traits = [t.strip() for t in traits.split(',') if t.strip()]

                # 3. Combine original data with AI-generated data
                data_object = {
                    "name": user_entry.get("name"),
                    "age": user_entry.get("age"),
                    "current_traits": traits,
                    "profile_summary": ai_results["profile_summary"], # AI Distilled
                    "embedding": ai_results["embedding"]             # AI Vector
                }

                # 4. Upload to Supabase
                user_id = self.user_db.add_data(data_object)
                
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