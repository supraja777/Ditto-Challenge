import streamlit as st

st.title("💘 Thursday: Date Feedback")

# 1. The Name
user_name = st.text_input("What is your name?")

# 2. The Logic
if user_name:
    st.write(f"### Hello, {user_name}!")
    
    choice = st.radio(
        "Do you want to go on a date again?",
        options=["Select...", "Yes", "No"]
    )

    if choice == "Yes":
        st.balloons()
        st.success("That's great! ❤️")
    elif choice == "No":
        st.info("You are closer to meeting your partner! ✨")