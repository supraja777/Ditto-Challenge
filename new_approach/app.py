from datetime import datetime
import json
import numpy as np
import pandas as pd

from app_logging import setup_matchmaking_loggers
from utils.generate_initial_score import generate_labeled_matrix
from utils.generate_initial_score import generate_judge_score_matrix

import os
system_log, ai_log = setup_matchmaking_loggers()

OUTPUT_DIR = "outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def save_matrix(df, prefix):
    """Saves a dataframe to the outputs folder with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(filepath)
    system_log.info(f"Matrix saved to {filepath}")
    return filepath

if __name__ == "__main__":
    try:
        df_matrix = generate_labeled_matrix('dummy_user_details.json', 'config.json')
        judge_score = generate_judge_score_matrix('dummy_user_details.json', 'config.json')
        
        print("\n--- MATCH CONFIDENCE MATRIX (Rows: User A, Cols: User B) ---")
        print("Note: Scores close to 1.0 are strong matches. -10.0 indicates a Deal Breaker.\n")
        print(df_matrix.to_string())
        
        # Quick view of best potential pairs
        print("\n--- HIGHEST RAW SCORES ---")
        unstacked = df_matrix.unstack().sort_values(ascending=False)
        print(unstacked[unstacked > 0].head(10))

        print("\n--- JUDGE CONFIDENCE MATRIX (Rows: User A, Cols: User B) ---")
        print("Note: Scores close to 1.0 are strong matches. -10.0 indicates a Deal Breaker.\n")
        print(judge_score.to_string())
        
        # Quick view of best potential pairs
        print("\n--- HIGHEST RAW SCORES ---")
        unstacked = judge_score.unstack().sort_values(ascending=False)
        print(unstacked[unstacked > 0].head(10))
       
        df_judge = pd.DataFrame(judge_score)
        df_matrix = pd.DataFrame(df_matrix)

        path_normal = save_matrix(df_matrix, "normal_score_matrix")
        path_judge = save_matrix(df_judge, "judge_score_matrix")
    except Exception as e:
        print(f"Error: {e}. Ensure JSON files are formatted correctly.")