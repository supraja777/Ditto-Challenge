import json
import os
from database import User

class PopulateUserData:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.user_db = User()

    def start_migration(self):
        """
        Reads the JSON file and iterates through each user to upload them.
        """
        if not os.path.exists(self.json_file_path):
            print(f"❌ Error: File {self.json_file_path} not found.")
            return

        try:
            with open(self.json_file_path, 'r') as f:
                users_data = json.load(f)

            print(f"🚀 Starting migration for {len(users_data)} users...")

            success_count = 0
            for index, user_entry in enumerate(users_data):
                # 1. Standardize the data object
                # If current_traits is a string in JSON, convert to list
                traits = user_entry.get("current_traits", [])
                if isinstance(traits, str):
                    traits = [t.strip() for t in traits.split(',') if t.strip()]

                data_object = {
                    "name": user_entry.get("name"),
                    "age": user_entry.get("age"),
                    "current_traits": traits,
                    "profile_summary": user_entry.get("profile_summary", ""),
                    "embedding": user_entry.get("embedding")
                }

                # 2. Send to User class for DB insertion
                user_id = self.user_db.add_data(data_object)
                
                if user_id:
                    success_count += 1
                    print(f"[{index+1}] Migrated: {data_object['name']}")
                else:
                    print(f"[{index+1}] Failed: {data_object['name']}")

            print(f"\n✅ Migration Complete! {success_count}/{len(users_data)} users uploaded.")

        except Exception as e:
            print(f"❌ Migration interrupted by error: {e}")

# --- Execution Script ---
if __name__ == "__main__":
    # Ensure this path matches where your JSON file is located
    JSON_PATH = "UserPool.json" 
    
    populator = PopulateUserData(JSON_PATH)
    populator.start_migration()