import os
import json
import numpy as np
from MatchMakingAgent import MatchmakingAgent
from DateSimulationAgent import DateSimulationAgent
# Your PersonaAgent is imported here
from PersonaAgent import PersonaAgent 

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
        Step 2 & 3: Find best matches, simulate, and pair exclusively.
        """
        # Ensure pool is ready
        if not self.processed_pool:
            self._prepare_pool()

        available_ids = [u['id'] for u in self.processed_pool]
        final_pairings = []

        # Iterate until no more pairs can be made
        while len(available_ids) > 1:
            # 1. Take the next available user
            uid_a = available_ids[0]
            user_a = next(u for u in self.processed_pool if u['id'] == uid_a)
            
            # 2. Get top mathematical candidates from the MatchmakingAgent
            # We filter for only 'available' IDs
            all_matches = self.matchmaker.get_top_matches(uid_a, top_k=10)
            valid_candidates = [m for m in all_matches if m['id'] in available_ids]
            
            # Narrow down to Top 3 for simulation to optimize API usage
            top_3 = valid_candidates[:3]
            
            best_sim_score = -1
            best_partner = None
            best_result = None

            # 3. Simulate conversations with the top candidates
            for candidate in top_3:
                user_b = next(u for u in self.processed_pool if u['id'] == candidate['id'])
                
                # Call DateSimulationAgent.simulate_date()
                sim_result = self.simulator.simulate_date(user_a, user_b)
                
                if sim_result['impression_score'] > best_sim_score:
                    best_sim_score = sim_result['impression_score']
                    best_partner = user_b
                    best_result = sim_result

            # 4. Finalize the best simulation as a pair
            if best_partner:
                final_pairings.append({
                    "user_a": user_a,
                    "user_b": best_partner,
                    "chemistry": best_sim_score,
                    "critique": best_result['critique'],
                    "transcript": best_result['transcript']
                })
                
                # CRITICAL: Remove both from availability
                available_ids.remove(uid_a)
                available_ids.remove(best_partner['id'])
            else:
                # Fallback: if no candidates found, move to next
                available_ids.remove(uid_a)

        return final_pairings