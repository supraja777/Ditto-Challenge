import streamlit as st
import time
import os
# Import your User class from your separate file
# from database_logic import User 

def save_feedback_to_supabase(name, feedback, energy, target="N/A"):
    """Bridges the UI to the Database class."""
    return 
    try:
        user_manager = User()
        user_id = user_manager.get_id_by_name(name)
        
        if user_id:
            # Updating traits based on feedback
            payload = {
                "social_energy": energy,
                "profile_summary": f"Feedback on {target}: {feedback}"
            }
            success = user_manager.update_traits(user_id, payload)
            if success:
                st.success("✅ Your feedback is collected and will be valued.")
                time.sleep(2)
                return True
        else:
            st.error(f"User '{name}' not found in database.")
            return False
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return False

def feedback_form():
    st.header("💘 Thursday: Date Feedback")

    # 1. Initialize 'step' and 'user_name' in session state 
    # This is crucial so the app remembers who you are between clicks
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""

    # --- STEP 1: Name Input ---
    if st.session_state.step == 1:
        st.write("Welcome to the feedback portal. Please identify yourself.")
        name_input = st.text_input("Your Name", placeholder="e.g. Supraja Srikanth")
        
        if st.button("Start Feedback"):
            if name_input:
                st.session_state.user_name = name_input
                st.session_state.step = 2
                st.rerun() # Forces Streamlit to refresh and show Step 2
            else:
                st.warning("Please enter your name to proceed.")

    # --- STEP 2: The Date Question ---
    elif st.session_state.step == 2:
        st.subheader(f"How was your date, {st.session_state.user_name}?")
        
        choice = st.radio(
            "Do you want to go on a date again with this person?",
            options=["Select...", "Yes", "No"],
            key="choice_radio"
        )

        # Handling "YES"
        if choice == "Yes":
            st.balloons()
            st.markdown("### ❤️❤️❤️ That's great!")
            if st.button("Save & Complete"):
                if save_feedback_to_supabase(st.session_state.user_name, "User said YES.", 10):
                    # Reset the form for the next user session
                    st.session_state.step = 1
                    st.session_state.user_name = ""
                    st.rerun()

        # Handling "NO"
        elif choice == "No":
            st.info("✨ You are closer to meeting your partner!")
            
            with st.container(border=True):
                st.write("### Tell us more")
                target_name = st.text_input("Who was your date with?")
                feedback_text = st.text_area("What would you like us to know? (Feedback)")
                energy_rating = st.select_slider("Your current social energy", options=range(1, 11), value=5)

                if st.button("Submit Weekly Feedback"):
                    if target_name and feedback_text:
                        if save_feedback_to_supabase(st.session_state.user_name, feedback_text, energy_rating, target_name):
                            st.session_state.step = 1
                            st.session_state.user_name = ""
                            st.rerun()
                    else:
                        st.error("Please fill in the partner's name and feedback details.")
        
        # Back button to Step 1
        st.divider()
        if st.button("⬅️ Back / Different User"):
            st.session_state.step = 1
            st.rerun()

