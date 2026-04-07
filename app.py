import streamlit as st
import json
import os
import pandas as pd
from database.User import User
from agents.Matches import Matches  # Ensure your class is in Matches.py

# Set page config
st.set_page_config(page_title="Ditto Matchmaker", page_icon="👥", layout="wide")

def load_users():
    """Fetches users directly from the Supabase database."""
    user_manager = User()
    
    try:
        users = user_manager.get_all_users()
        st.session_state.all_users = users
        return users
    except Exception as e:
        st.error(f"Failed to load users from database: {e}")
        return []

# Persistent state for results
if "final_matches" not in st.session_state:
    st.session_state.final_matches = []

if "users" not in st.session_state:
    st.session_state.users = load_users()

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
            st.warning("No users found in the database.")
        else:
            st.success(f"Found {len(users)} users!")
            
            # 1. Convert to a Pandas DataFrame for better control
            df = pd.DataFrame(users)
            # st.write("Database Columns Found:", df.columns.tolist())
   
            # 2. Select and rename columns to match your UI needs
            # Mapping database keys to display names
            df_display = df[['name', 'age', 'current_traits', 'profile_summary']]

            # 3. Display using st.dataframe with custom widths
            st.dataframe(
                df_display,
                column_config={
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Age": st.column_config.NumberColumn("Age", width="small"),
                    "Traits": st.column_config.ListColumn("Traits", width="medium"),
                    "Summary": st.column_config.TextColumn("Summary", width="large"),
                },
                hide_index=True,
                use_container_width=True # This makes the whole table fill the screen width
            )

# --- BUTTON 2: MAKE MATCHES ---
with col_btn2:
    if st.button("🚀 Make Matches", use_container_width=True, type="primary"):
        raw_users = load_users()
        
        if not raw_users or len(raw_users) < 2:
            st.error("Need at least 2 users to create a match!")
        else:
            # 1. Trigger the logic via the Matches class
            with st.spinner("Agents are collaborating to find the best pairs..."):
                orchestrator = Matches()
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
                st.write(f"Traits: *{match['user_a']['current_traits']}*")
            
            with col_heart:
                st.markdown("<h2 style='text-align: center;'>❤️</h2>", unsafe_allow_html=True)
                # Note: using 'chemistry_score' to match your class output
                st.metric("Chemistry Score", f"{match['chemistry_score']}%")
            
            with col_b:
                st.subheader(match['user_b']['name'])
                st.write(f"Traits: *{match['user_b']['current_traits']}*")
            
            st.success(f"**Agent Critique:** {match['critique']}")
            with st.expander("Read Date Transcript"):
                st.text(match['transcript'])

# # --- Independent Feedback Section ---
# # --- Independent Feedback Section ---
# st.divider()
# st.header("🔄 Manual Date Feedback")
# st.info("Update User B's traits based on feedback given by User A.")

# # Load fresh data from Supabase into the session state
# from agents.FeedbackAgent import FeedbackAgent
# feedback_agent = FeedbackAgent()

# if "all_users" in st.session_state:
#     # Creating a list of names and a map to get the full user object
#     user_names = [u['name'] for u in st.session_state.all_users]
#     user_map = {u['name']: u for u in st.session_state.all_users}

#     with st.form("manual_feedback_form", clear_on_submit=True):
#         # 1. Feedback Provider (User A)
#         person_a_name = st.selectbox("Feedback Provider (User A)", options=user_names)
        
#         # 2. Person being Reviewed (User B) - This is the person who will be UPDATED
#         remaining_names = [n for n in user_names if n != person_a_name]
#         match_name = st.selectbox("Person being Reviewed (User B)", options=remaining_names)
        
#         # 3. The feedback content
#         feedback_reason = st.text_area(f"What did {person_a_name} say about {match_name}?")

#         submit_btn = st.form_submit_button("Update User B's Traits")

#     if submit_btn:
#         if not feedback_reason.strip():
#             st.error("Please provide feedback text before updating.")
#         else:
#             # We target User B (match_name) for the update
#             user_b_to_update = user_map[match_name]
            
#             with st.spinner(f"Updating traits for {match_name}..."):
#                 # Call your function targeting User B's current traits
#                 new_traits = feedback_agent.update_user_traits(
#                     user_id = user_b_to_update.get('id'),
#                     current_traits=user_b_to_update.get('current_traits'),
#                     match_name=person_a_name, # User A is the 'match' in this context
#                     feedback_reason=feedback_reason
#                 )
            
#             st.success(f"Success! {match_name}'s traits have been evolved.")
#             # This triggers a rerun so the 'load_users()' at the top 
#             # fetches the new traits and updates the dropdowns immediately
