import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_all_user_details():
    """
    Fetches all columns for all users from the Supabase 'users' table.
    Returns: List of dictionaries (one per user).
    """
    try:
        response = supabase.table("users").select("*").execute()
        
        if response.data:
            return response.data
        return []

    except Exception as e:
        st.error(f"❌ Failed to fetch user details: {e}")
        return []

def get_user_by_name(user_name):
    """
    Helper to find a specific user's data by their name.
    """
    try:
        response = supabase.table("users")\
            .select("*")\
            .eq("user_name", user_name)\
            .maybe_single()\
            .execute()
            
        return response.data
    except Exception as e:
        print(f"❌ Error fetching user {user_name}: {e}")
        return None