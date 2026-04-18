import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_all_matches():
    """
    Fetches all matches from the database and resolves IDs to User Names.
    Returns a list of dicts: {userNameA, userNameB, confidence_score, match_id}
    """
    try:
        response = supabase.table("matches").select(
            "id",
            "confidence_score",
            "user_a_id",
            "user_b_id"
        ).execute()

        raw_matches = response.data
        formatted_matches = []

        users_response = supabase.table("users").select("id", "user_name").execute()
        user_map = {u['id']: u['user_name'] for u in users_response.data}

        for match in raw_matches:
            formatted_matches.append({
                "match_id": match["id"],
                "userNameA": user_map.get(match["user_a_id"], "Unknown"),
                "userNameB": user_map.get(match["user_b_id"], "Unknown"),
                "confidence_score": match["confidence_score"]
            })

        return formatted_matches

    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
        return []

if __name__ == "__main__":
    matches = get_all_matches()
    for m in matches:
        print(f"{m['userNameA']} ❤️ {m['userNameB']} | Score: {m['confidence_score']}")