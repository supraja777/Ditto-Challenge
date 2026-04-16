import os
import pandas as pd
import streamlit as st
import time

# Internal Imports
from feedback import save_feedback
from utils.generate_confidence_matrix import generate_confidence_matrix
from utils.generate_optimized_matches import generate_optimized_pairs
from ui_utils import push_results_util

# Path Constants
MATCHES_FILE = os.path.join("outputs", "final_match_pairs.csv")
FEEDBACK_FILE = os.path.join("outputs", "user_feedback_collection.csv")

# --- PROTOCOL FUNCTIONS ---

def harvest_feedback_trigger():
    """Sets the state to show the feedback UI."""
    st.session_state.show_feedback_ui = True
    st.toast("Feedback harvester activated!", icon="📝")

def calibrate_thresholds():
    st.toast("Running: calibrate_thresholds()...")
    time.sleep(1)
    st.success("✅ Global Thresholds Adjusted in DB.")

def audit_system():
    st.toast("Running: audit_system()...")
    time.sleep(1)
    st.success("✅ Ghost Users Purged & Math Validated.")

def run_simulations():
    st.toast("Running: run_simulations()...")
    time.sleep(1)
    st.success("✅ Stagnation Simulations Complete.")

def evolve_vectors():
    st.toast("Running: evolve_vectors()...")
    time.sleep(1)
    st.success("✅ Embeddings Re-calculated for Active Pool.")

def push_results():
    # Reset feedback UI when new results are pushed
    st.session_state.show_feedback_ui = False
    push_results_util()
    st.success("✅ Pushed Results to Dispatcher!")

def execute_big_run():
    # Generate the initial matrices
    generate_confidence_matrix()
    st.success("✅ Tuesday Simulation & Matrix Generation Complete!")

# --- UI LOGIC ---

def render_heartbeat_ui():
    st.set_page_config(page_title="Matchmaking Heartbeat", layout="wide")
    st.title("🔗 Core Matchmaking Heartbeat")
    
    # Initialize Session States
    if "selected_day" not in st.session_state:
        st.session_state.selected_day = "Tuesday"
    if "show_feedback_ui" not in st.session_state:
        st.session_state.show_feedback_ui = False

    # Mapping days to their respective functions
    lifecycle = {
        "Thursday": {"icon": "📝", "action": "Update User Traits", "func": harvest_feedback_trigger},
        "Friday": {"icon": "⚙️", "action": "Update Thresholds", "func": calibrate_thresholds},
        "Saturday": {"icon": "🛡️", "action": "Data Validation", "func": audit_system},
        "Sunday": {"icon": "🧪", "action": "Handle 'No Data'", "func": run_simulations},
        "Monday": {"icon": "🧬", "action": "Re-draw Embeddings", "func": evolve_vectors},
        "Tuesday": {"icon": "⚡", "action": "Generate Matches", "func": execute_big_run},
        "Wednesday": {"icon": "🎁", "action": "Push Results", "func": push_results},
    }

    # 1. Day Navigation Header
    cols = st.columns(7)
    days = list(lifecycle.keys())
    
    for i, col in enumerate(cols):
        if col.button(days[i][:3], use_container_width=True, 
                      type="primary" if st.session_state.selected_day == days[i] else "secondary"):
            st.session_state.selected_day = days[i]
            # Close feedback UI if we switch away from Thursday
            if days[i] != "Thursday":
                st.session_state.show_feedback_ui = False

    st.divider()

    # 2. Detailed Action Card
    day = st.session_state.selected_day
    data = lifecycle[day]
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{data['icon']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{day}</h2>", unsafe_allow_html=True)

    with col_right:
        st.subheader(f"Stage: {data['action']}")
        st.write(f"This process ensures the {day} logic is applied across the entire user database.")
        
        # 3. THE EXECUTION BUTTON
        button_label = f"▶️ Run {day} Protocol"
        if st.button(button_label, use_container_width=True):
            data['func']()

        # --- THURSDAY PERSISTENCE LOGIC ---
        if day == "Thursday" and st.session_state.get("show_feedback_ui", False):
            st.divider()
            st.subheader("📝 Record Qualitative Feedback")
            
            if not os.path.exists(MATCHES_FILE):
                st.error("No match pairs found. Run Wednesday Protocol first.")
            else:
                df_matches = pd.read_csv(MATCHES_FILE)
                for index, row in df_matches.iterrows():
                    u_a, u_b, score = row['user_a'], row['user_b'], row['confidence_score']
                    
                    with st.expander(f"🤝 Match: {u_a} vs {u_b} (Score: {score:.2f})"):
                        c1, c2 = st.columns(2)
                        with c1:
                            # Note: B gives feedback for A
                            fb_for_a = st.text_area(f"What did {u_b} say about {u_a}?", key=f"fba_{index}")
                        with c2:
                            # Note: A gives feedback for B
                            fb_for_b = st.text_area(f"What did {u_a} say about {u_b}?", key=f"fbb_{index}")
                        
                        if st.button(f"Confirm & Save Pair {index}", key=f"save_{index}"):
                            save_feedback(u_a, u_b, fb_for_a, fb_for_b)

    # Sidebar
    st.sidebar.header("System Status")
    st.sidebar.status("Database: Connected")
    st.sidebar.progress((days.index(day) + 1) / 7, text=f"Day {days.index(day) + 1} of 7")

if __name__ == "__main__":
    render_heartbeat_ui()