import streamlit as st
import time

from utils.generate_confidence_matrix import generate_confidence_matrix
from utils.generate_optimized_matches import generate_optimized_pairs
from ui_utils import push_results_util

# --- MOCK FUNCTIONS (Placeholders for your Agents) ---

def harvest_feedback():
    st.toast("Running: harvest_feedback()...")
    print("EXECUTE: harvest_feedback()")
    time.sleep(1)
    st.success("✅ Feedback Harvested and Traits Updated.")

def calibrate_thresholds():
    st.toast("Running: calibrate_thresholds()...")
    print("EXECUTE: calibrate_thresholds()")
    time.sleep(1)
    st.success("✅ Global Thresholds Adjusted in DB.")

def audit_system():
    st.toast("Running: audit_system()...")
    print("EXECUTE: audit_system()")
    time.sleep(1)
    st.success("✅ Ghost Users Purged & Math Validated.")

def run_simulations():
    st.toast("Running: run_simulations()...")
    print("EXECUTE: run_simulations()")
    time.sleep(1)
    st.success("✅ Stagnation Simulations Complete.")

def evolve_vectors():
    st.toast("Running: evolve_vectors()...")
    print("EXECUTE: evolve_vectors()")
    time.sleep(1)
    st.success("✅ Embeddings Re-calculated for Active Pool.")

def push_results():
    st.toast("Pushing: Results!...")
    print("EXECUTE: push_results()")
    push_results_util()
    st.success("✅ Pushed Results. All the best!")

def execute_big_run():
    st.toast("Executing: Results!...")
    print("EXECUTE: Executning big ()")
    generate_confidence_matrix()
    st.success("✅ Pushed Results. All the best!")

# --- UI LOGIC ---

def render_heartbeat_ui():
    st.title("🔗 Core Matchmaking Heartbeat")
    
    # Mapping days to their respective functions
    lifecycle = {
        "Thursday": {"icon": "📝", "action": "Update User Traits", "func": harvest_feedback},
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
    
    if "selected_day" not in st.session_state:
        st.session_state.selected_day = "Tuesday"

    for i, col in enumerate(cols):
        if col.button(days[i][:3], use_container_width=True, 
                      type="primary" if st.session_state.selected_day == days[i] else "secondary"):
            st.session_state.selected_day = days[i]

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
            # Dynamically call the function mapped to this day
            data['func']()

    st.sidebar.header("System Status")
    st.sidebar.status("Database: Connected")
    st.sidebar.progress((days.index(day) + 1) / 7, text=f"Day {days.index(day) + 1} of 7")

if __name__ == "__main__":
    render_heartbeat_ui()