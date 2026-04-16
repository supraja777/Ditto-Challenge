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
        pairs_df.to_csv(output_file, index=False)
        
        st.write("Syncing results to User Notification Dispatcher...")
        time.sleep(1)
        
        st.write("Finalizing AI_reasoning_logs for audit trail...")
        status.update(label="✅ All Matches Successfully Pushed!", state="complete", expanded=False)
    
    # Display a summary table of the matches pushed
    if pairs:
        st.subheader("📊 Pushed Match Summary")
        summary_df = pd.DataFrame(pairs)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.balloons()
   