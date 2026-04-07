import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import random
import streamlit as st
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()
class MatchmakingAgent:
    def __init__(self):
        self.user_pool = [] # List of persona_packets

    def get_embedding(self, text):
        """
        Generates a 384-dimensional vector locally.
        """
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if not text:
            return np.zeros(384)
        
        # This runs on your CPU/GPU instantly
        embedding = model.encode(text)
        return embedding

    def _parse_embedding(self, embedding_data):
        """
        HELPER: This is the 'stripper' that removes the quotes.
        It turns "[0.1, 0.2]" (String) into [0.1, 0.2] (List).
        """
        if isinstance(embedding_data, str):
            try:
                return json.loads(embedding_data)
            except Exception as e:
                print(f"❌ Error parsing embedding string: {e}")
                return None
        return embedding_data

    def add_to_pool(self, persona_packet: dict):
        self.user_pool.append(persona_packet)

    def _calculate_age_score(self, age_a, age_b):
        """Returns a score from 0 to 1 based on age proximity."""
        diff = abs(age_a - age_b)
        if diff <= 5: return 1.0
        if diff <= 10: return 0.7
        return 0.3
    
    def _calculate_trait_bonus(self, traits_a, traits_b):
        """
        Semantic Trait Bonus: Compares the vector distance between 
        two sets of traits using their own embeddings.
        """
        if not traits_a or not traits_b:
            print("No traits?")
            return 0.0

        # 1. Generate Embeddings for the raw trait strings
        # (Assuming you have a self.get_embedding helper)
        vec_a = self.get_embedding(traits_a)
        vec_b = self.get_embedding(traits_b)

        # 2. Calculate Similarity
        # Reshape for sklearn if necessary
        vec_a = np.array(vec_a).reshape(1, -1)
        vec_b = np.array(vec_b).reshape(1, -1)
        
        semantic_sim = float(cosine_similarity(vec_a, vec_b)[0][0])

        # 3. Apply a Scaling Factor
        # We don't want the bonus to be as big as the main score.
        # A 0.10 max bonus is usually a good 'nudge'.
        bonus = semantic_sim * 0.10

        print("Trait bonus --", bonus)
        
        return round(bonus, 4)


    import random

    def get_top_matches(self, target_id, top_k=5, epsilon=0.1, threshold=0.5):
        target = next((u for u in self.user_pool if u['id'] == target_id), None)
        if not target: return []

        # --- 1. DECIDE: EXPLORE VS EXPLOIT ---
        # epsilon=0.1 means 10% chance to pick a random wildcard
        if random.random() < epsilon:
            st.info("🎲 EXPLORATION MODE: Picking a wildcard match to learn more about you.")
            pool = [u for u in self.user_pool if u['id'] != target_id]
            random.shuffle(pool)
            
            # Return wildcards in the same format as scored matches for UI consistency
            return [{
                "id": u['id'],
                "name": u.get('name', 'Unknown'),
                "final_score": 0.0, # Flag as exploration
                "metrics": {"type": "Discovery"},
                "summary": u.get('profile_summary', '')
            } for u in pool[:top_k]]

        # --- 2. EXPLOITATION MODE ---
        st.success("🎯 EXPLOITATION MODE: Finding your highest-probability matches.")
        scored_matches = []
        
        target_list = self._parse_embedding(target.get('embedding'))
        target_vec = np.array(target_list).reshape(1, -1)      

        for candidate in self.user_pool:
            if candidate['id'] == target_id:
                continue

            candidate_vec = self._parse_embedding(candidate.get('embedding'))
            candidate_vec = np.array(candidate_vec).reshape(1, -1)
            
            # Calculate Cosine Similarity
            cos_sim = float(cosine_similarity(target_vec, candidate_vec)[0][0])
            
            # --- 3. APPLY THRESHOLD BIAS ---
            # If the vibe is below our threshold, we don't even consider them
            if cos_sim < threshold:
                continue

            # Scores from your existing logic
            age_score = self._calculate_age_score(target.get('age', 0), candidate.get('age', 0))
            trait_bonus = self._calculate_trait_bonus(target.get('current_traits', ''), candidate.get('current_traits', ''))

            # Final Weighted Score (70/20/10)
            final_score = (cos_sim * 0.7) + (age_score * 0.2) + (trait_bonus)
            final_score = min(1.0, final_score)

            scored_matches.append({
                "id": candidate['id'],
                "name": candidate.get('name', 'Unknown'),
                "final_score": round(final_score, 4),
                "metrics": {
                    "vibe_similarity": round(cos_sim, 4),
                    "age_alignment": age_score
                },
                "summary": candidate.get('profile_summary', '')
            })

        # Sort by final score descending
        scored_matches.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scored_matches[:top_k]