from supabase import create_client, Client
import os

# Initialize Supabase client (Ensure these are in your .env or streamlit secrets)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def upload_matches_to_supabase(final_pairs):
    """
    Accepts the list of pair dictionaries and uploads them to the 'matches' table.
    """
    if not final_pairs:
        print("No pairs to upload.")
        return

    print(f"🚀 Initializing DB Upload for {len(final_pairs)} pairs...")
    
    success_count = 0
    
    for pair in final_pairs:
        try:
            # We use upsert to prevent duplicates if user_a and user_b already exist as a pair
            # This matches the schema we created (user_a_id, user_b_id, confidence_score)
            data = {
                "user_a_id": pair["user_a_id"],
                "user_b_id": pair["user_b_id"],
                "confidence_score": pair["confidence_score"],
                "accepted": False  # Default state for Wednesday
            }

            print("What is the data?? ", data)
            
            # Using .upsert() requires a unique constraint on (user_a_id, user_b_id) 
            # in Supabase to work perfectly, otherwise use .insert()
            response = supabase.table("matches").insert(data).execute()

            print("What is teh repsinse ", response)
            
            success_count += 1
            print(f"✅ Uploaded: {pair['user_a_id']} x {pair['user_b_id']}")
            
        except Exception as e:
            print(f"❌ Failed to upload pair {pair['user_a_id']}-{pair['user_b_id']}: {e}")

    print(f"🏁 Database Sync Complete. {success_count}/{len(final_pairs)} pairs live.")