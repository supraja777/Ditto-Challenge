import os
import json
import random
import numpy as np
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from database.Config import Config

load_dotenv()

class MatchmakingAgent:
    def __init__(self):
        self.user_pool = [] 
        # Load model once during init to save memory and time
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.config_manager = Config()

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
       
        cfg = self.config_manager.load_all_thresholds() 

        w_vibe = cfg.get('weight_vibe', 0.40)
        w_traits = cfg.get('weight_traits', 0.15)
        w_intellect = cfg.get('weight_intellect', 0.15)
        w_age = cfg.get('weight_age', 0.10)
        e_bonus_val = cfg.get('social_energy_bonus', 0.05)
        h_bonus_unit = cfg.get('hobby_bonus_unit', 0.02)

        # --- LAYER 1: HARD FILTERS ---
        a_dealbreakers = [d.lower() for d in user_a.get('dealbreakers', [])]
        b_traits = [t.lower() for t in user_b.get('current_traits', [])]
        
        # If a hard filter is hit, return 0s immediately
        if any(trait in a_dealbreakers for trait in b_traits):
            return 0.0, 0.0, 0.0
        
        if user_a.get('intent') != user_b.get('intent'):
            return 0.0, 0.0, 0.0 

        # --- LAYER 2: VECTOR CALCULATIONS ---
        # Similarity between the profile summaries
        vibe_sim = self.get_cosine_similarity(user_a.get('embedding'), user_b.get('embedding'))
        # Similarity between the trait lists
        trait_sim = self.get_cosine_similarity(user_a.get('trait_embedding'), user_b.get('trait_embedding'))

        # --- LAYER 3: HEURISTIC BONUSES ---
        
        # 1. Social Energy (Balance Logic)
        energy_gap = abs(user_a.get('social_energy', 5) - user_b.get('social_energy', 5))
        energy_bonus = e_bonus_val if 3 <= energy_gap <= 6 else 0
        
        # 2. Intellectual Alignment (Live Embedding comparison)
        intellect_sim = self.get_cosine_similarity(
            self.get_embedding(user_a.get('intellectual_focus', '')),
            self.get_embedding(user_b.get('intellectual_focus', ''))
        )

        # 3. Hobby Overlap
        shared_hobbies = set(user_a.get('hobbies', [])) & set(user_b.get('hobbies', []))
        hobby_bonus = len(shared_hobbies) * h_bonus_unit

        # 4. Age Alignment
        age_score = self._calculate_age_score(user_a.get('age', 0), user_b.get('age', 0))

        # --- LAYER 4: THE FINAL AGGREGATION ---
        final_score = (
            (vibe_sim * w_vibe) + 
            (trait_sim * w_traits) + 
            (intellect_sim * w_intellect) + 
            (age_score * w_age) +
            (energy_bonus) + 
            (hobby_bonus)
        )
        
        # Return the score, the vibe similarity, and age score for the UI/Metrics
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