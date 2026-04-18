from supabase import create_client, Client
import os

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def update_match_feedback(match_id, feedback_text, for_user_a=True, accepted=True):
    """
    Updates a specific match record with feedback and acceptance status.
    
    Args:
        match_id (str): The UUID of the match record.
        feedback_text (str): The feedback string provided by the AI/User.
        for_user_a (bool): If True, updates 'feedback_for_a', else 'feedback_for_b'.
        accepted (bool): The final acceptance state of the match.
    """
    try:
        feedback_column = "feedback_for_a" if for_user_a else "feedback_for_b"
        
        update_data = {
            feedback_column: feedback_text,
            "accepted": accepted
        }

        response = supabase.table("matches")\
            .update(update_data)\
            .eq("id", match_id)\
            .execute()

        if response.data:
            print(f"✅ Match {match_id} updated successfully.")
            return response.data
        else:
            print(f"⚠️ No match found with ID: {match_id}")
            return None

    except Exception as e:
        print(f"❌ Error updating match feedback: {e}")
        return None

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
            data = {
                "user_a_id": pair["user_a_id"],
                "user_b_id": pair["user_b_id"],
                "confidence_score": pair["confidence_score"],
                "accepted": False
            }

            print("What is the data?? ", data)
            
            response = supabase.table("matches").insert(data).execute()

            print("What is teh repsinse ", response)
            
            success_count += 1
            print(f"✅ Uploaded: {pair['user_a_id']} x {pair['user_b_id']}")
            
        except Exception as e:
            print(f"❌ Failed to upload pair {pair['user_a_id']}-{pair['user_b_id']}: {e}")

    print(f"🏁 Database Sync Complete. {success_count}/{len(final_pairs)} pairs live.")