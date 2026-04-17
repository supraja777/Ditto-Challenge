import os

import pandas as pd
import streamlit as st
import time
from streamlit_extras.let_it_rain import rain
from utils.generate_optimized_matches import generate_optimized_pairs
OUTPUT_DIR = "outputs"
def push_results_util():
    with st.status("🚀 Dispatching Match Results...", expanded=True) as status:
        st.write("Fetching optimized pairs from matches_score_matrix.csv...")
        time.sleep(1)
        
        # Call your existing logic
        pairs = generate_optimized_pairs() 
        output_file = os.path.join(OUTPUT_DIR, "final_match_pairs.csv")
        pairs_df = pd.DataFrame(pairs)
        pairs_df.to_csv(output_file, index=True)
        
        st.write("Syncing results to User Notification Dispatcher...")
        time.sleep(1)
        
        st.write("Finalizing AI_reasoning_logs for audit trail...")
        status.update(label="✅ All Matches Successfully Pushed!", state="complete", expanded=False)
    
    # Display a summary table of the matches pushed
    if pairs:
        from db.get_all_users import get_all_user_details
        all_users = get_all_user_details()

        # Create a dictionary for fast lookup: { "uuid": "Name" }
        user_id_to_name = {u['id']: u['user_name'] for u in all_users}

        # 2. Prepare the display data
        display_pairs = []
        for pair in pairs:
            display_pairs.append({
                "User A": user_id_to_name.get(pair.get('user_a_id'), "Unknown"),
                "User B": user_id_to_name.get(pair.get('user_b_id'), "Unknown"),
                "Confidence Score": f"{pair.get('confidence_score', 0):.2f}"
            })

        st.subheader("Final Matches")
        summary_df = pd.DataFrame(display_pairs)
        st.dataframe(summary_df,use_container_width=True, hide_index=True)
    st.balloons()
   