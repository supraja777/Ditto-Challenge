import streamlit as st
import json
import os
import pandas as pd
from Matches import Matches  # Ensure your class is in Matches.py

# Set page config
st.set_page_config(page_title="Ditto Matchmaker", page_icon="👥", layout="wide")

# Persistent state for results
if "final_matches" not in st.session_state:
    st.session_state.final_matches = []

def load_users():
    """Loads users from the persistent JSON file."""
    if os.path.exists("UserPool.json"):
        with open("UserPool.json", "r") as f:
            return json.load(f)
    return []

# --- UI Layout ---
st.title("👥 Matchmaking Agent: User Pool")
st.write("Manage your persona database and generate AI-simulated dates.")

# Create Two Buttons side-by-side
col_btn1, col_btn2 = st.columns(2)

# --- BUTTON 1: SHOW USERS ---
with col_btn1:
    if st.button("Show User Pool", use_container_width=True):
        users = load_users()
        if not users:
            st.warning("No users found in UserPool.json.")
        else:
            st.success(f"Found {len(users)} users in the pool!")
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

# --- BUTTON 2: MAKE MATCHES ---
with col_btn2:
    if st.button("🚀 Make Matches", use_container_width=True, type="primary"):
        raw_users = load_users()
        
        if not raw_users or len(raw_users) < 2:
            st.error("Need at least 2 users to create a match!")
        else:
            # 1. Trigger the logic via the Matches class
            with st.spinner("Agents are collaborating to find the best pairs..."):
                orchestrator = Matches(raw_users)
                # This triggers the full pipeline: Preparation -> Simulation -> Matching
                st.session_state.final_matches = orchestrator.generate_exclusive_pairs()
            
            st.balloons()
            st.success("Matchmaking complete!")

# --- RESULTS DISPLAY ---
if st.session_state.final_matches:
    st.divider()
    st.header("🏆 AI-Generated Final Pairs")
    
    for match in st.session_state.final_matches:
        with st.container(border=True):
            col_a, col_heart, col_b = st.columns([2, 1, 2])
            
            with col_a:
                st.subheader(match['user_a']['name'])
                st.write(f"Traits: *{match['user_a']['traits']}*")
            
            with col_heart:
                st.markdown("<h2 style='text-align: center;'>❤️</h2>", unsafe_allow_html=True)
                # Note: using 'chemistry_score' to match your class output
                st.metric("Chemistry Score", f"{match['chemistry_score']}%")
            
            with col_b:
                st.subheader(match['user_b']['name'])
                st.write(f"Traits: *{match['user_b']['traits']}*")
            
            st.success(f"**Agent Critique:** {match['critique']}")
            with st.expander("Read Date Transcript"):
                st.text(match['transcript'])