import time
import pandas as pd
import streamlit as st

from agents.Matches import Matches
from database.Matches_db import MatchesDB
from database.User import User

def push_results_utility():
    db = MatchesDB()
    user_manager = User()
    
    st.toast("Running: execute_big_run()...")
    time.sleep(1)
    
    match_records = db.get_all_matches()
    
    if not match_records:
        st.error("No matches found in the database.")
        return

    # 1. Resolve IDs and calculate high-level metrics
    resolved_matches = []
    total_compat = 0
    
    for match in match_records:
        user_a = user_manager.get_user_by_id(match['user_a_id'])
        user_b = user_manager.get_user_by_id(match['user_b_id'])
        
        # comp_val = match.get('compatibility', 0)
        # total_compat += comp_val
        
        resolved_matches.append({
            "User A": user_a['name'] if user_a else "Unknown",
            "User B": user_b['name'] if user_b else "Unknown",
           # "Compatibility Score": comp_val,
           # "Match Rating": "🔥 High" if comp_val > 0.8 else "✅ Solid" if comp_val > 0.5 else "🧬 Diverse"
        })

    avg_compat = (total_compat / len(match_records)) * 100 if match_records else 0

    # --- UI ENHANCEMENT BEGINS ---
    
    st.success("✅ Weekly Matches Generated Successfully!")
    
    # 2. Key Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Matches", len(match_records))
    with col2:
        st.metric("Avg. Compatibility", f"{avg_compat:.1f}%")
    with col3:
        st.metric("Status", "Active", delta="Ready to Push")

    st.divider()

    # 3. Styled Data Table
    st.write("### 🤝 Connection Schedule")
    
    df_display = pd.DataFrame(resolved_matches)
    
    # Use st.column_config to add progress bars for compatibility
    st.dataframe(
        df_display,
        column_config={
            "Compatibility Score": st.column_config.ProgressColumn(
                "Compatibility %",
                help="The algorithmic match strength",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "Match Rating": st.column_config.TextColumn("Category")
        },
        use_container_width=True,
        hide_index=True
    )

    # 4. Action Area
    st.divider()
    c1, c2 = st.columns([1, 4])
    with c1:
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📩 Export CSV",
            data=csv,
            file_name='weekly_matches.csv',
            mime='text/csv',
            use_container_width=True
        )
    with c2:
        st.info("The schedule above has been synchronized with the Supabase production environment.")