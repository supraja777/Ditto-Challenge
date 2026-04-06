import streamlit as st
import json
import os
import pandas as pd

# Import your classes
from PersonaAgent import PersonaAgent
from MatchMakingAgent import MatchmakingAgent
from DateSimulationAgent import DateSimulationAgent

# Set page config
st.set_page_config(page_title="Ditto Matchmaker", page_icon="👥", layout="wide")

# Initialize Agents in Session State
if "p_agent" not in st.session_state:
    st.session_state.p_agent = PersonaAgent()
    st.session_state.m_agent = MatchmakingAgent()
    st.session_state.sim_agent = DateSimulationAgent()
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
            
            # Displaying users in a clean table format
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

            st.divider()
            st.subheader("Detailed Persona View")
            for u in users:
                with st.expander(f"View Profile: {u['name']} ({u['id']})"):
                    st.write(f"**Age:** {u['age']}")
                    st.write(f"**Traits:** {u['traits']}")
                    st.write(f"**Vibe Summary:** {u['profile_summary']}")

# --- BUTTON 2: MAKE MATCHES ---
with col_btn2:
    if st.button("🚀 Make Matches", use_container_width=True, type="primary"):
        raw_users = load_users()
        
        if not raw_users or len(raw_users) < 2:
            st.error("Need at least 2 users to create a match!")
        else:
            with st.status("Agents are collaborating...", expanded=True) as status:
                
                # 1. PERSONA PHASE: Create embeddings for the pool
                st.write("🧠 **PersonaAgent**: Analyzing psychological profiles...")
                processed_pool = []
                for user in raw_users:
                    # Distill and embed via PersonaAgent
                    packet = st.session_state.p_agent.create_embedding(user)
                    # Re-attach meta for MatchmakingAgent heuristics
                    packet.update({
                        "name": user['name'], 
                        "age": user.get('age', 0), 
                        "traits": user.get('traits', '')
                    })
                    processed_pool.append(packet)
                    st.session_state.m_agent.add_to_pool(packet)

                # 2. MATCHMAKING & SIMULATION PHASE: Exclusive Pairing
                st.write("🎯 **Matchmaking**: Finding best mathematical vibes...")
                available_ids = [u['id'] for u in processed_pool]
                pairings = []

                while len(available_ids) > 1:
                    uid_a = available_ids[0]
                    user_a = next(u for u in processed_pool if u['id'] == uid_a)
                    
                    # Find candidates currently still 'on the market'
                    candidates = st.session_state.m_agent.get_top_matches(uid_a, top_k=5)
                    valid_candidates = [c for c in candidates if c['id'] in available_ids]
                    
                    if not valid_candidates:
                        available_ids.remove(uid_a)
                        continue

                    # Pick #1 Match and validate via Simulation
                    top_match_data = valid_candidates[0]
                    user_b = next(u for u in processed_pool if u['id'] == top_match_data['id'])
                    
                    st.write(f"🎭 **Simulation**: Dating {user_a['name']} & {user_b['name']}...")
                    sim_result = st.session_state.sim_agent.simulate_date(user_a, user_b)
                    
                    pairings.append({
                        "a": user_a,
                        "b": user_b,
                        "score": sim_result['impression_score'],
                        "critique": sim_result['critique'],
                        "transcript": sim_result['transcript']
                    })
                    
                    # Remove from pool
                    available_ids.remove(uid_a)
                    available_ids.remove(user_b['id'])

                st.session_state.final_matches = pairings
                status.update(label="All dates simulated and matched!", state="complete")

# --- RESULTS DISPLAY ---
if st.session_state.final_matches:
    st.divider()
    st.header("🏆 AI-Generated Final Pairs")
    
    for match in st.session_state.final_matches:
        with st.container(border=True):
            col_a, col_heart, col_b = st.columns([2, 1, 2])
            with col_a:
                st.subheader(match['a']['name'])
                st.write(f"Traits: *{match['a']['traits']}*")
            with col_heart:
                st.markdown("<h2 style='text-align: center;'>❤️</h2>", unsafe_allow_html=True)
                st.metric("Chemistry Score", f"{match['score']}%")
            with col_b:
                st.subheader(match['b']['name'])
                st.write(f"Traits: *{match['b']['traits']}*")
            
            st.success(f"**Agent Critique:** {match['critique']}")
            with st.expander("Read Date Transcript"):
                st.text(match['transcript'])