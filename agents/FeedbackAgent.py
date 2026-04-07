import os
from groq import Groq
from dotenv import load_dotenv
from database.User import User  # Import your DB manager

load_dotenv()

class FeedbackAgent:
    def __init__(self):
        """
        Initializes the Groq client and the Database manager.
        """
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.db_manager = User() # Initialize Supabase connection

    def update_user_traits(self, user_id, current_traits, match_name, feedback_reason):
        """
        Takes existing traits, evolves them via LLM, and SAVES them to the database.
        
        Args:
            user_id (str): The unique ID of the user being updated (User B).
            current_traits (str): User B's current traits.
            match_name (str): The name of User A (the reviewer).
            feedback_reason (str): The feedback text.
        """
        print(f"--- Evolving traits for User ID: {user_id} ---")
        
        prompt = (
            f"User's Current Traits: {current_traits}\n"
            f"Feedback from {match_name}: '{feedback_reason}'.\n\n"
            f"Task: Produce a new, updated list of traits for this user.\n"
            f"1. Retain the core identity.\n"
            f"2. Incorporate specific preferences based on the feedback.\n"
            f"3. Result must be a concise, comma-separated string.\n"
            f"4. Result MUST contain LESS than 6 main traits.\n"
            f"Return ONLY the new traits string, no conversational filler."
        )

        try:
            # 1. Generate new traits using LLM
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a psychological profiling engine that evolves personality traits based on social feedback."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.4
            )
            
            evolved_traits = response.choices[0].message.content.strip()
            print(f"Old: {current_traits} -> New: {evolved_traits}")

            # 2. UPDATE THE DATABASE
            # We assume your database column is named 'Traits'
            payload = {"current_traits": evolved_traits}

            result = self.db_manager.update_traits(user_id, payload)
        

            if result:
                print(f"Successfully updated database for {user_id}")
                return evolved_traits
            else:
                print("Database update failed (no result returned).")
                return current_traits

        except Exception as e:
            print(f"Error in FeedbackAgent: {e}")
            return current_traits

if __name__ == "__main__":
    # Test block
    agent = FeedbackAgent()
    # Replace with a real ID from your Supabase to test
    test_id = "2135d298-ad74-4ac0-ab920-00c08d36e568" 
    old = "Introverted, Creative, Analytical"
    match = "Alex"
    msg = "Alex was too loud and hyper-active."
    
    agent.update_user_traits(test_id, old, match, msg)