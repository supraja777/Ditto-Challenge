import streamlit as st
import json
import os

# Set page config
st.set_page_config(page_title="Matchmaking User Pool", page_icon="👥")

def load_users():
    """Loads users from the persistent JSON file."""
    if os.path.exists("UserPool.json"):
        with open("UserPool.json", "r") as f:
            return json.load(f)
    return []

# --- UI Layout ---
st.title("👥 Matchmaking Agent: User Pool")
st.write("Click the button below to view all personas currently in the database.")

# The Button
if st.button("Show Users"):
    users = load_users()
    
    if not users:
        st.warning("No users found in UserPool.json. Please run your population script first.")
    else:
        st.success(f"Found {len(users)} users in the pool!")
        
        # Displaying users in a clean table format
        # We exclude 'embedding' from the display to keep it readable
        display_data = []
        for u in users:
            display_data.append({
                "ID": u['id'],
                "Name": u['name'],
                "Age": u['age'],
                "Traits": u['traits'],
                "Summary": u['profile_summary']
            })
            
        st.table(display_data)

        # Alternative: Detailed Card View
        st.divider()
        st.subheader("Detailed Persona View")
        for u in users:
            with st.expander(f"View Profile: {u['name']} ({u['id']})"):
                st.write(f"**Age:** {u['age']}")
                st.write(f"**Traits:** {u['traits']}")
                st.write(f"**Vibe Summary:** {u['profile_summary']}")