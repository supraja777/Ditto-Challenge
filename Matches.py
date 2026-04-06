import os
import json
import numpy as np
from MatchMakingAgent import MatchmakingAgent
from DateSimulationAgent import DateSimulationAgent
# Your PersonaAgent is imported here
from PersonaAgent import PersonaAgent 
import streamlit as st

class Matches:
    def __init__(self, raw_user_data):
        """
        raw_user_data: List of dicts (e.g., from UserPool.json or a CSV)
        """
        self.raw_data = raw_user_data
        self.persona_agent = PersonaAgent()
        self.matchmaker = MatchmakingAgent()
        self.simulator = DateSimulationAgent()
        self.processed_pool = []

    def _prepare_pool(self):
        """
        Step 1: Convert raw text into AI-distilled personas and vectors.
        """
        st.write("🧠 Distilling personas and generating embeddings...")
        for user in self.raw_data:
            # Call your PersonaAgent.create_embedding()
            persona_packet = self.persona_agent.create_embedding(user)
            
            # Re-attach metadata for the MatchmakingAgent's heuristics (Age/Traits)
            persona_packet.update({
                "name": user.get('name'),
                "age": user.get('age', 0),
                "traits": user.get('traits', '')
            })
            
            self.processed_pool.append(persona_packet)
            self.matchmaker.add_to_pool(persona_packet)
        
        st.success(f"Successfully processed {len(self.processed_pool)} personas.")

    def generate_exclusive_pairs(self):
        """
        Orchestrates the Matchmaking and Simulation agents to create 
        one-to-one pairings from the user pool.
        """
        # 1. Ensure the pool has been processed by PersonaAgent
        if not self.processed_pool:
            self._prepare_pool()

        # Track IDs of users who haven't been matched yet
        available_ids = [u['id'] for u in self.processed_pool]
        final_pairings = []

        print(f"🚀 Starting Exclusive Matchmaking for {len(available_ids)} users...")

        # 2. Main Matching Loop
        while len(available_ids) > 1:
            # Pick the next person needing a match
            uid_a = available_ids[0]
            user_a = next(u for u in self.processed_pool if u['id'] == uid_a)
            
            # 3. Call MatchmakingAgent to find top candidates
            # We ask for a larger k (e.g., 10) to ensure we find enough 'available' users
            all_potential_matches = self.matchmaker.get_top_matches(uid_a, top_k=3)
            
            # Filter results: Only candidates who are still in available_ids
            valid_candidates = [m for m in all_potential_matches if m['id'] in available_ids]
            
            # Use the Top 3 valid mathematical matches for the simulation
            top_3_to_simulate = valid_candidates[:3]
            
            if not top_3_to_simulate:
                # If no one in the remaining pool meets the matchmaker's criteria
                print(f"⚠️ No suitable matches found for {user_a['name']}. Skipping.")
                available_ids.remove(uid_a)
                continue

            best_sim_score = -1
            best_partner_profile = None
            best_result_packet = None

            # 4. Simulation Logic: Test the 'Chemistry' of the top candidates
            for candidate in top_3_to_simulate:
                user_b = next(u for u in self.processed_pool if u['id'] == candidate['id'])
                
                print(f"🎭 Simulating Date: {user_a['name']} + {user_b['name']}...")
                
                # Execute the conversation and evaluation
                sim_result = self.simulator.simulate_date(user_a, user_b)
                
                # Check if this is the best simulation so far for User A
                if sim_result['impression_score'] > best_sim_score:
                    best_sim_score = sim_result['impression_score']
                    best_partner_profile = user_b
                    best_result_packet = sim_result

            # 5. Finalize the Pairing
            if best_partner_profile:
                final_pairings.append({
                    "user_a": user_a,
                    "user_b": best_partner_profile,
                    "chemistry_score": best_sim_score,
                    "critique": best_result_packet['critique'],
                    "transcript": best_result_packet['transcript']
                })
                
                print(f"✅ MATCH CONFIRMED: {user_a['name']} & {best_partner_profile['name']}")
                
                # Remove BOTH users from the available list
                available_ids.remove(uid_a)
                available_ids.remove(best_partner_profile['id'])
            else:
                # Fallback: remove User A if no partner could be simulated
                available_ids.remove(uid_a)

        # 6. Handle the "Odd Person Out"
        if len(available_ids) == 1:
            leftover = next(u for u in self.processed_pool if u['id'] == available_ids[0])
            print(f"ℹ️ {leftover['name']} remains unmatched.")

        return final_pairings
