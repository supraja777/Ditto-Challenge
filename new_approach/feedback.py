import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Path to the matches generated on Wednesday
MATCHES_FILE = os.path.join("outputs", "final_match_pairs.csv")
FEEDBACK_FILE = os.path.join("outputs", "raw_feedback_collection.csv")

def render_feedback_ui():
    st.title("Thursday: Feedback Harvester")
    st.markdown("### 📝 Post-Date Debrief")
    st.write("Review the weekly matches and record qualitative feedback for trait evolution.")

    if not os.path.exists(MATCHES_FILE):
        st.error("No match pairs found. Please run the Wednesday 'Push Results' protocol first.")
        return

    # Load the pairs
    df_matches = pd.read_csv(MATCHES_FILE)

    # UI for the match list
    for index, row in df_matches.iterrows():
        user_a = row['user_a']
        user_b = row['user_b']
        score = row['confidence_score']

        # Create a "Match Card" using an expander
        with st.expander(f"🤝 Match: {user_a} x {user_b} (Score: {score:.2f})"):
            st.info(f"Record the interaction details for this pair to update their behavioral vectors.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"From {user_b}")
                feedback_b = st.text_area(
                    f"How did {user_b} perceive {user_a}?", 
                    key=f"fb_{user_b}_{user_a}",
                    placeholder="e.g., 'Arjun was very analytical but a bit too quiet...'"
                )
            
            with col2:
                st.subheader(f"From {user_a}")
                feedback_a = st.text_area(
                    f"How did {user_a} perceive {user_b}?", 
                    key=f"fb_{user_a}_{user_b}",
                    placeholder=f"e.g., '{user_b} had great energy and matched my focus...'"
                )

            if st.button(f"Save Feedback for {user_a} & {user_b}", key=f"btn_{index}"):
                save_feedback(user_a, user_b, feedback_a, feedback_b)

def save_feedback(a, b, feedback_for_a, feedback_for_b):
    """
    Saves feedback in the specific format: user_a, user_b, feedback_for_a, feedback_for_b
    """
    # Validation: Don't save if both fields are empty
    if not feedback_for_a.strip() and not feedback_for_b.strip():
        st.warning("Please enter feedback for at least one user before saving.")
        return

    # Prepare the data row
    # Note: 'feedback_for_a' is what USER_B said about USER_A
    new_entry = pd.DataFrame([{
        "user_a": a,
        "user_b": b,
        "feedback_for_a": feedback_for_a.strip(),
        "feedback_for_b": feedback_for_b.strip(),
        "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M") # Useful for Friday sorting
    }])
    
    # Path to your collection file
    COLLECTION_FILE = os.path.join("outputs", "user_feedback_collection.csv")
    
    # Append logic
    file_exists = os.path.isfile(COLLECTION_FILE)
    new_entry.to_csv(COLLECTION_FILE, mode='a', index=False, header=not file_exists)
    
    st.toast(f"Feedback archived for {a} & {b}", icon="📁")
    st.success(f"✅ Successfully recorded feedback for the {a}-{b} interaction.")

if __name__ == "__main__":
    render_feedback_ui()