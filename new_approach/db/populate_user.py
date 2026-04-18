import json
import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def upload_dummy_users(json_file_path):
    if not os.path.exists(json_file_path):
        print(f"❌ Error: File not found at {json_file_path}")
        return

    with open(json_file_path, 'r') as f:
        users_data = json.load(f)

    print(f"🚀 Found {len(users_data)} users. Syncing to Supabase...")

    for user in users_data:
        try:
            generated_id = str(uuid.uuid4())
            payload = {
                "id": generated_id,
                "user_name": user.get("user_name"),
                "age": user.get("age"),
                "location": user.get("location"),
                "personality": user.get("personality"),
                "intellectual_focus": user.get("intellectual_focus"),
                "intent": user.get("intent"),
                "social_energy": user.get("social_energy"),
                "traits": user.get("traits"),          
                "deal_breakers": user.get("deal_breakers"), 
                "trait_embeddings": user.get("trait_embeddings"),    
                "personality_embedding": user.get("personality_embedding")
            }

            supabase.table("users").upsert(payload).execute()
            print(f"✅ Successfully synced user: {user.get('user_name')} ({user.get('id')})")

        except Exception as e:
            print(f"❌ Failed to sync {user.get('user_name')}: {e}")

    print("🏁 Sync complete.")

if __name__ == "__main__":
    PATH_TO_JSON = os.path.join("./", "dummy_user_details.json")
    upload_dummy_users(PATH_TO_JSON)