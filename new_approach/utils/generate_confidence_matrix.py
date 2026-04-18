from datetime import datetime
import json
import random
import numpy as np
import pandas as pd

from app_logging import setup_matchmaking_loggers
from db.get_all_users import get_all_user_details
from utils.generate_initial_score import generate_labeled_matrix
from utils.generate_initial_score import generate_judge_score_matrix

import os
system_log, ai_log = setup_matchmaking_loggers()

OUTPUT_DIR = "outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

with open('config.json', 'r') as f:
    config = json.load(f)

def save_matrix(df, prefix):
    """Saves a dataframe to the outputs folder with a timestamp."""
    filename = f"{prefix}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(filepath, index = True)
    system_log.info(f"Matrix saved to {filepath}")
    return filepath

def generate_confidence_matrix():
    try:
        users = get_all_user_details()
        df_matrix = generate_labeled_matrix(users, 'config.json')
        judge_score = generate_judge_score_matrix(users, 'config.json')
        
        print("\n--- MATCH CONFIDENCE MATRIX (Rows: User A, Cols: User B) ---")
        print("Note: Scores close to 1.0 are strong matches. -10.0 indicates a Deal Breaker.\n")
        print(df_matrix.to_string())
        
        print("\n--- HIGHEST RAW SCORES ---")
        unstacked = df_matrix.unstack().sort_values(ascending=False)
        print(unstacked[unstacked > 0].head(10))

        print("\n--- JUDGE CONFIDENCE MATRIX (Rows: User A, Cols: User B) ---")
        print("Note: Scores close to 1.0 are strong matches. -10.0 indicates a Deal Breaker.\n")
        print(judge_score.to_string())
        
        print("\n--- HIGHEST RAW SCORES ---")
        unstacked = judge_score.unstack().sort_values(ascending=False)
        print(unstacked[unstacked > 0].head(10))
       
        df_judge = pd.DataFrame(judge_score)
        df_matrix = pd.DataFrame(df_matrix)
        name_to_id = {u['user_name']: u['id'] for u in users}
        ids = [name_to_id.get(name) for name in df_matrix.index]

        df_matrix.index = pd.MultiIndex.from_tuples(list(zip(ids, df_matrix.index)), names=['id', 'name'])
        df_matrix.columns = pd.MultiIndex.from_tuples(list(zip(ids, df_matrix.columns)), names=['id', 'name'])

        df_judge.index = pd.MultiIndex.from_tuples(list(zip(ids, df_judge.index)), names=['id', 'name'])
        df_judge.columns = pd.MultiIndex.from_tuples(list(zip(ids, df_judge.columns)), names=['id', 'name'])

        path_normal = save_matrix(df_matrix, "normal_score_matrix")
        path_judge = save_matrix(df_judge, "judge_score_matrix")

        df_final = (df_matrix * config['weights']['w_normal']) + (df_judge * config['weights']['w_judge'])

        exploration_rate = config['matching_logic'].get('exploration_rate', 0.1)

        if random.random() < exploration_rate:
            # --- EXPLORE MODE ---
            # Adding noise to shuffle the rankings
            noise = np.random.uniform(-0.15, 0.15, size=df_final.shape)
            df_final = (df_final + noise)
            print("🎲 Strategy: EXPLORATION (Noise injected to discover new patterns)")
        else:
            # --- EXPLOIT MODE ---
            # No noise
            print("🎯 Strategy: EXPLOITATION (Strict adherence to calculated weights)")

        # Normalizing values.
        min_val = df_final.values.min()
        max_val = df_final.values.max()

        if max_val > min_val:
            df_final = (df_final - min_val) / (max_val - min_val)
        else:
            df_final = df_final / max_val if max_val != 0 else df_final
        path_final_matrix = save_matrix(df_final, "matches_score_matrix")

    except Exception as e:
        print(f"Error: {e}. Ensure JSON files are formatted correctly.")