import os
import json
import random
import numpy as np
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class MatchmakingAgent:
    def __init__(self):
        self.user_pool = [] 
        # Load model once during init to save memory and time
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_embedding(self, text):
        """Generates a 384-dimensional vector locally."""
        if not text:
            return np.zeros(384)
        # model.encode returns a numpy array
        return self.model.encode(text)

    def get_cosine_similarity(self, vec_a, vec_b):
        """Helper to handle reshaping and similarity calculation."""
        if vec_a is None or vec_b is None:
            return 0.0
        
        # Ensure they are numpy arrays and 2D for sklearn
        a = np.array(self._parse_embedding(vec_a)).reshape(1, -1)
        b = np.array(self._parse_embedding(vec_b)).reshape(1, -1)
        
        return float(cosine_similarity(a, b)[0][0])

    def calculate_rich_score(self, user_a, user_b):
        """The 7-factor Rich Computation logic."""
        # --- LAYER 1: HARD FILTERS ---
        # Fixed: Check for dealbreakers in traits (ensure case-insensitive)
        a_dealbreakers = [d.lower() for d in user_a.get('dealbreakers', [])]
        b_traits = [t.lower() for t in user_b.get('current_traits', [])]
        
        if any(trait in a_dealbreakers for trait in b_traits):
            return 0, 0, 0
        
        if user_a.get('intent') != user_b.get('intent'):
            return 0, 0, 0 

        # --- LAYER 2: VECTOR CALCULATIONS (The "Vibe") ---
        vibe_sim = self.get_cosine_similarity(user_a.get('embedding'), user_b.get('embedding'))
        trait_sim = self.get_cosine_similarity(user_a.get('trait_embedding'), user_b.get('trait_embedding'))

        # --- LAYER 3: HEURISTIC BONUSES ---
        
        # 1. Social Energy (Targeting a "Balance")
        energy_gap = abs(user_a.get('social_energy', 5) - user_b.get('social_energy', 5))
        energy_bonus = 0.05 if 3 <= energy_gap <= 6 else 0
        
        # 2. Intellectual Alignment
        intellect_sim = self.get_cosine_similarity(
            self.get_embedding(user_a.get('intellectual_focus', '')),
            self.get_embedding(user_b.get('intellectual_focus', ''))
        )

        # 3. Hobby Overlap
        a_hobbies = set(user_a.get('hobbies', []))
        b_hobbies = set(user_b.get('hobbies', []))
        shared_hobbies = a_hobbies & b_hobbies
        hobby_bonus = len(shared_hobbies) * 0.02

        # 4. Age Alignment (Using your helper)
        age_score = self._calculate_age_score(user_a.get('age', 0), user_b.get('age', 0))

        # --- LAYER 4: THE FINAL AGGREGATION ---
        final_score = (
            (vibe_sim * 0.40) + 
            (trait_sim * 0.15) + 
            (intellect_sim * 0.15) + 
            (age_score * 0.10) +
            (energy_bonus) + 
            (hobby_bonus)
        )
        
        return min(1.0, final_score), vibe_sim, age_score

    def _parse_embedding(self, embedding_data):
        """Converts strings or nested lists into flat lists/arrays."""
        if isinstance(embedding_data, str):
            try:
                return json.loads(embedding_data)
            except:
                return None
        # If it's a nested list like [[...]], flatten it
        if isinstance(embedding_data, (list, np.ndarray)) and len(embedding_data) > 0:
            if isinstance(embedding_data[0], (list, np.ndarray)):
                return embedding_data[0]
        return embedding_data

    def _calculate_age_score(self, age_a, age_b):
        diff = abs(age_a - age_b)
        if diff <= 5: return 1.0
        if diff <= 10: return 0.7
        return 0.3

    def add_to_pool(self, persona_packet: dict):
        self.user_pool.append(persona_packet)

    def get_top_matches(self, target_id, top_k=5, epsilon=0.1):
        target = next((u for u in self.user_pool if u['id'] == target_id), None)
        if not target: return []

        # --- 1. EXPLORATION MODE ---
        if random.random() < epsilon:
            st.info("🎲 EXPLORATION MODE")
            pool = [u for u in self.user_pool if u['id'] != target_id]
            random.shuffle(pool)
            return [{
                "id": u['id'],
                "name": u.get('name', 'Unknown'),
                "final_score": 0.0,
                "metrics": {"type": "Discovery"},
                "summary": u.get('profile_summary', '')
            } for u in pool[:top_k]]

        # --- 2. EXPLOITATION MODE ---
        st.success("🎯 EXPLOITATION MODE")
        scored_matches = []
        
        for candidate in self.user_pool:
            if candidate['id'] == target_id:
                continue
            
            # Fixed: Call using self. and unpack the returned values
            final_score, v_sim, a_score = self.calculate_rich_score(target, candidate)

            scored_matches.append({
                "id": candidate['id'],
                "name": candidate.get('name', 'Unknown'),
                "final_score": round(final_score, 4),
                "metrics": {
                    "vibe_similarity": round(v_sim, 4),
                    "age_alignment": a_score
                },
                "summary": candidate.get('profile_summary', '')
            })

        scored_matches.sort(key=lambda x: x['final_score'], reverse=True)
        return scored_matches[:top_k]