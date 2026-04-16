import json
import numpy as np
import pandas as pd
import streamlit as st  # Added Streamlit import
import time

from utils.Date_Simulation import date_simulation

def generate_judge_score_matrix(users_file, config_file):
    # Load the two input files
    with open(users_file, 'r') as f:
        users = json.load(f)
    with open(config_file, 'r') as f:
        config = json.load(f)

    n = len(users)
    names = [u['user_name'] for u in users]
    judge_matrix = np.full((n, n), -1.0)

    st.info(f"🚀 Initializing Full Mesh Simulation for **{n} users**...")
    
    # Using st.status to create a clean, collapsible log
    with st.status("Running AI Date Simulations...", expanded=True) as status:
        total_sims = (n * (n - 1)) // 2
        count = 0
        progress_bar = st.progress(0)

        for i in range(n):
            for j in range(i + 1, n):
                user_a = users[i]['user_name']
                user_b = users[j]['user_name']
                
                # Update UI text
                st.write(f"🎭 Simulating: **{user_a}** & **{user_b}**")
                
                # Execute simulation
                simulated_judge_score = date_simulation(users[i], users[j], 1) 
                
                judge_matrix[i][j] = simulated_judge_score
                judge_matrix[j][i] = simulated_judge_score
                
                # Update progress
                count += 1
                progress_bar.progress(count / total_sims)
        
        status.update(label="✅ Simulation Complete!", state="complete", expanded=False)

    df_judge = pd.DataFrame(judge_matrix, index=names, columns=names)
    return df_judge

def cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    if np.all(v1 == 0) or np.all(v2 == 0):
        return 0.0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def generate_labeled_matrix(users_file, config_file):
    with open(users_file, 'r') as f:
        users = json.load(f)
    with open(config_file, 'r') as f:
        config = json.load(f)

    n = len(users)
    names = [u['user_name'] for u in users]
    matrix = np.zeros((n, n))
    
    weights = config['weights']
    c = config['constraints']

    st.write("🧪 Calculating Math/Embedding Scores...")
    
    # Mini-progress bar for the math matrix
    math_progress = st.progress(0)

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = -1.0 
                continue
            
            user_a, user_b = users[i], users[j]

            # 1. Deal Breakers
            a_breakers = set(user_a.get('deal_breakers', []))
            b_traits = set(user_b.get('traits', []))
            if not a_breakers.isdisjoint(b_traits):
                matrix[i][j] = -10.0 
                continue

            # 2. Embedding similarities
            pers_sim = cosine_similarity(user_a['personality_embedding'], user_b['personality_embedding'])
            trait_sim = cosine_similarity(user_a['trait_embeddings'], user_b['trait_embeddings'])

            # 3. Scalar Scoring
            age_score = max(0, 1 - (abs(user_a['age'] - user_b['age']) / c['max_age_diff']))
            loc_score = 1.0 if user_a['location'] == user_b['location'] else 0.0
            energy_score = 1 - (abs(user_a['social_energy'] - user_b['social_energy']) / 10.0)
            intel_score = 1.0 if user_a['intellectual_focus'] == user_b['intellectual_focus'] else 0.0

            # 4. Final Aggregation
            score = (
                (pers_sim * weights['personality_embedding_w']) +
                (trait_sim * weights['traits_embedding_w']) +
                (age_score * weights['age_w']) +
                (loc_score * weights['location_w']) +
                (energy_score * weights['social_energy_w']) +
                (intel_score * weights['intellectual_w'])
            )

            if user_a['intent'] != user_b['intent']:
                score -= c['penalty_for_intent_mismatch']

            matrix[i][j] = round(score + config['embedding_config']['bias'], 3)
        
        # Update math progress bar
        math_progress.progress((i + 1) / n)

    st.success("✅ Mathematical Matrix Compiled.")
    df = pd.DataFrame(matrix, index=names, columns=names)
    return df