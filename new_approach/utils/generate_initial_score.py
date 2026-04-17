import ast
import json
import numpy as np
import pandas as pd
import streamlit as st
import time

from utils.Date_Simulation import date_simulation

def generate_judge_score_matrix(users, config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    n = len(users)
    names = [u['user_name'] for u in users]
    # Initialize with float type to avoid ufunc errors later
    judge_matrix = np.full((n, n), -1.0, dtype=float)

    st.info(f"🚀 Initializing Full Mesh Simulation for **{n} users**...")
    
    with st.status("Running AI Date Simulations...", expanded=True) as status:
        total_sims = (n * (n - 1)) // 2
        count = 0
        progress_bar = st.progress(0)

        for i in range(n):
            for j in range(i + 1, n):
                user_a_name = users[i]['user_name']
                user_b_name = users[j]['user_name']
                
                st.write(f"🎭 Simulating: **{user_a_name}** & **{user_b_name}**")
                
                # Execute simulation - ensure result is cast to float
                try:
                    simulated_judge_score = float(date_simulation(users[i], users[j], 1))
                except (ValueError, TypeError):
                    simulated_judge_score = 0.0
                
                judge_matrix[i][j] = simulated_judge_score
                judge_matrix[j][i] = simulated_judge_score
                
                count += 1
                progress_bar.progress(min(count / total_sims, 1.0))
        
        status.update(label="✅ Simulation Complete!", state="complete", expanded=False)

    return pd.DataFrame(judge_matrix, index=names, columns=names)

def ensure_float_list(v):
    """Converts string representation of lists into actual lists of floats."""
    if isinstance(v, str):
        try:
            # Turns "[0.1, 0.2]" into [0.1, 0.2]
            v = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return np.zeros(4) # Fallback to zero vector if parsing fails
    return np.array(v, dtype=float)

def cosine_similarity(v1, v2):
    # CRITICAL: Parse strings into lists, then convert to numpy arrays
    v1 = ensure_float_list(v1)
    v2 = ensure_float_list(v2)
    
    if np.all(v1 == 0) or np.all(v2 == 0):
        return 0.0
    
    norm = (np.linalg.norm(v1) * np.linalg.norm(v2))
    if norm == 0:
        return 0.0
        
    return float(np.dot(v1, v2) / norm)

def generate_labeled_matrix(users, config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    n = len(users)
    names = [u['user_name'] for u in users]
    matrix = np.zeros((n, n), dtype=float)
    
    weights = config.get('weights', {})
    c = config.get('constraints', {})
    bias = config.get('embedding_config', {}).get('bias', 0.0)

    st.write("🧪 Calculating Math/Embedding Scores...")
    math_progress = st.progress(0)

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = -1.0 
                continue
            
            user_a, user_b = users[i], users[j]

            # 1. Deal Breakers (disjoint returns True if no common elements)
            a_breakers = set(user_a.get('deal_breakers') or [])
            b_traits = set(user_b.get('traits') or [])
            if not a_breakers.isdisjoint(b_traits):
                matrix[i][j] = -10.0 
                continue

            # 2. Embedding similarities
            pers_sim = cosine_similarity(user_a.get('personality_embedding', []), user_b.get('personality_embedding', []))
            trait_sim = cosine_similarity(user_a.get('trait_embeddings', []), user_b.get('trait_embeddings', []))

            # 3. Scalar Scoring - with safety checks for missing config
            max_age_diff = c.get('max_age_diff', 20)
            age_diff = abs(float(user_a.get('age', 0)) - float(user_b.get('age', 0)))
            age_score = max(0.0, 1.0 - (age_diff / max_age_diff))
            
            loc_score = 1.0 if user_a.get('location') == user_b.get('location') else 0.0
            
            energy_diff = abs(float(user_a.get('social_energy', 5)) - float(user_b.get('social_energy', 5)))
            energy_score = 1.0 - (energy_diff / 10.0)
            
            intel_score = 1.0 if user_a.get('intellectual_focus') == user_b.get('intellectual_focus') else 0.0

            # 4. Final Aggregation using float casting for weights
            score = (
                (pers_sim * float(weights.get('personality_embedding_w', 0))) +
                (trait_sim * float(weights.get('traits_embedding_w', 0))) +
                (age_score * float(weights.get('age_w', 0))) +
                (loc_score * float(weights.get('location_w', 0))) +
                (energy_score * float(weights.get('social_energy_w', 0))) +
                (intel_score * float(weights.get('intellectual_w', 0)))
            )

            if user_a.get('intent') != user_b.get('intent'):
                score -= float(c.get('penalty_for_intent_mismatch', 0))

            matrix[i][j] = round(score + float(bias), 3)
        
        math_progress.progress((i + 1) / n)

    st.success("✅ Mathematical Matrix Compiled.")
    return pd.DataFrame(matrix, index=names, columns=names)