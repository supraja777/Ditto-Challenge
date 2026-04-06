import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

class FeedbackAgent:
    def __init__(self):
        """
        Initializes the Groq client for LLM-based trait evolution.
        """
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def update_user_traits(self, current_traits, match_name, feedback_reason):
        """
        Takes existing traits and feedback, then produces a new evolved trait string.
        
        Args:
            current_traits (str): The user's current comma-separated traits.
            match_name (str): The name of the person they matched with.
            feedback_reason (str): The explanation for why it was a negative match.
            
        Returns:
            str: The updated/evolved traits string.
        """
        print("IN feedback agent")
        prompt = (
            f"User's Current Traits: {current_traits}\n"
            f"Negative Match Feedback: The user disliked a match with {match_name} because: '{feedback_reason}'.\n\n"
            f"Task: Produce a new, updated list of traits for this user. "
            f"1. Retain the core positive identity of the user.\n"
            f"2. Incorporate specific 'anti-traits' or preferences based on the feedback reason.\n"
            f"3. Ensure the result is a concise, comma-separated string suitable for embedding generation.\n"
            f"4. Ensure the result contains only 5 main traits that covers both current traits and the feeedback reason.\n"
            f"Return ONLY the new traits string, no conversational filler."
        )

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a psychological profiling engine that evolves personality traits based on social feedback."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.4
            )
            
            # Clean up the response to ensure it's just the string
            evolved_traits = response.choices[0].message.content.strip()
            print("Evolved traits == ", evolved_traits)
            return evolved_traits

        except Exception as e:
            print(f"Error evolving traits: {e}")
            return current_traits # Fallback to original traits on error
        

if __name__ == "__main__":
    # 1. Setup initial state
    agent = FeedbackAgent()
    old_traits = "Software Engineer, Introverted, Loves Coffee, Calm, Analytical"
    failed_match = "Alex"
    reason = "Alex was extremely loud, hyper-active, and didn't stop talking about extreme sports."

    print(f"DEBUG: Original Traits -> {old_traits}")
    
    # 2. Run the evolution
    updated_traits = agent.update_user_traits(old_traits, failed_match, reason)
    
    # 3. Show Results
    print("-" * 30)
    print(f"DEBUG: Evolved Traits  -> {updated_traits}")
    print("-" * 30)
    
    if len(updated_traits.split(',')) > len(old_traits.split(',')):
        print("Success: New preferences were likely added to the trait string.")
        print("Updated traits : ", updated_traits)