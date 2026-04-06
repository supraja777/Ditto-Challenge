import os
import streamlit as st
from database.User import User
from PersonaAgent import PersonaAgent
from MatchMakingAgent import MatchmakingAgent
from DateSimulationAgent import DateSimulationAgent

class Matches:
    def __init__(self):
        """
        Initializes the Matchmaking system by pulling the latest 
        user pool directly from the Supabase Cloud.
        """
        self.user_manager = User()
        self.persona_agent = PersonaAgent()
        self.matchmaker = MatchmakingAgent()
        self.simulator = DateSimulationAgent()
        
        # 1. Sync with Cloud: Pull the latest processed users
        self.processed_pool = self.user_manager.get_all_users()
        
        # 2. Feed the Matchmaker: Internalize the pool for vector math
        if not self.processed_pool:
            print("⚠️ Warning: User pool is empty. Did you run PopulateUserData?")
        else:
            for user in self.processed_pool:
                # The matchmaker needs these to calculate cosine similarity
                self.matchmaker.add_to_pool(user)
            print(f"✅ Matches initialized with {len(self.processed_pool)} users from Supabase.")

    def generate_exclusive_pairs(self):
        """
        Orchestrates the Matchmaking and Simulation agents to create 
        one-to-one pairings. Each user can only have ONE match.
        """
        # Track IDs of users who haven't been matched yet
        available_ids = [u['id'] for u in self.processed_pool]
        final_pairings = []

        print(f"🚀 Starting Exclusive Matchmaking for {len(available_ids)} users...")
        st.write(f"🚀 Starting Exclusive Matchmaking for {len(available_ids)} users...")

        # --- Main Matching Loop ---
        while len(available_ids) > 1:
            # Pick the first person in the list to find a match for
            uid_a = available_ids[0]
            user_a = next(u for u in self.processed_pool if u['id'] == uid_a)
            
            # 1. Ask Matchmaker for the top mathematical candidates
            # We fetch 10 to ensure we have enough 'available' backups
            all_potential_matches = self.matchmaker.get_top_matches(uid_a, top_k=10)
            
            # 2. Filter: Must be currently available AND NOT the user themselves
            valid_candidates = [
                m for m in all_potential_matches 
                if m['id'] in available_ids and m['id'] != uid_a
            ]
            
            # Use the Top 3 valid candidates for the 'Chemistry' simulation
            top_3_to_simulate = valid_candidates[:3]
            
            if not top_3_to_simulate:
                print(f"⚠️ No suitable partners left for {user_a['name']}. Moving to next.")
                available_ids.remove(uid_a)
                continue

            best_sim_score = -1
            best_partner_profile = None
            best_result_packet = None

            # 3. Simulation Logic: Test 'Chemistry' via LLM conversation
            for candidate in top_3_to_simulate:
                user_b = next(u for u in self.processed_pool if u['id'] == candidate['id'])
                
                print(f"🎭 Simulating Date: {user_a['name']} + {user_b['name']}...")
                st.write(f"🎭 Simulating Date: {user_a['name']} + {user_b['name']}...")
                
                # The simulator generates a transcript and an impression_score
                sim_result = self.simulator.simulate_date(user_a, user_b)
                
                # Identify the partner with the highest chemistry for User A
                if sim_result['impression_score'] > best_sim_score:
                    best_sim_score = sim_result['impression_score']
                    best_partner_profile = user_b
                    best_result_packet = sim_result

            # 4. Finalize the Pairing
            if best_partner_profile:
                final_pairings.append({
                    "user_a": user_a,
                    "user_b": best_partner_profile,
                    "chemistry_score": best_sim_score,
                    "critique": best_result_packet['critique'],
                    "transcript": best_result_packet['transcript']
                })
                
                print(f"✅ MATCH CONFIRMED: {user_a['name']} & {best_partner_profile['name']}")
                st.write(f"✅ MATCH CONFIRMED: {user_a['name']} & {best_partner_profile['name']}")
                
                # REMOVE BOTH users so they aren't matched again
                available_ids.remove(uid_a)
                available_ids.remove(best_partner_profile['id'])
            else:
                # If simulation fails for some reason, remove User A to prevent infinite loop
                available_ids.remove(uid_a)

        # 5. Handle the "Odd Person Out"
        if len(available_ids) == 1:
            leftover = next(u for u in self.processed_pool if u['id'] == available_ids[0])
            print(f"ℹ️ {leftover['name']} remains unmatched (Odd number of users).")
            st.write(f"ℹ️ {leftover['name']} remains unmatched (Odd number of users).")

        return final_pairings

# --- Test Script ---
if __name__ == "__main__":
    orchestrator = Matches()
    results = orchestrator.generate_exclusive_pairs()
    print(f"\n✨ Total Pairs Created: {len(results)}")