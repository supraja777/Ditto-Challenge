import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MatchmakingAgent:
    def __init__(self):
        self.user_pool = [] # List of persona_packets

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
        Simple heuristic: Check for specific complementary or 
        identical traits that historically work well.
        """
        bonus = 0
        t1, t2 = traits_a.lower(), traits_b.lower()
        
        # Example: Introvert/Extrovert balance
        if ("introvert" in t1 and "extrovert" in t2) or ("extrovert" in t1 and "introvert" in t2):
            bonus += 0.05
        
        # Example: Shared High Openness
        if "creative" in t1 and "creative" in t2:
            bonus += 0.05
            
        return bonus

    def get_top_matches(self, target_id, top_k=5):
        target = next((u for u in self.user_pool if u['id'] == target_id), None)
        if not target: return []

        scored_matches = []
        target_vec = np.array(target['embedding']).reshape(1, -1)

        for candidate in self.user_pool:
            if candidate['id'] == target_id:
                continue

            candidate_vec = np.array(candidate['embedding']).reshape(1, -1)
            
            # 1. Cosine Similarity (The "Vibe" Vector)
            cos_sim = float(cosine_similarity(target_vec, candidate_vec)[0][0])
            
            # 2. Age Factor
            age_score = self._calculate_age_score(target.get('age', 0), candidate.get('age', 0))
            
            # 3. Trait Factor
            trait_bonus = self._calculate_trait_bonus(target.get('traits', ''), candidate.get('traits', ''))

            # 4. Final Weighted Score
            # Weights: 70% Vibe, 20% Age, 10% Traits
            final_score = (cos_sim * 0.7) + (age_score * 0.2) + (trait_bonus)
            final_score = min(1.0, final_score) # Cap at 1.0

            scored_matches.append({
                "id": candidate['id'],
                "name": candidate.get('name', 'Unknown'),
                "final_score": round(final_score, 4),
                "metrics": {
                    "vibe_similarity": round(cos_sim, 4),
                    "age_alignment": age_score
                },
                "summary": candidate['profile_summary']
            })

        # Sort by final score descending
        scored_matches.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scored_matches[:top_k]