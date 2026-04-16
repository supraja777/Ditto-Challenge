import json
import numpy as np
import pandas as pd

from utils.generate_initial_score import generate_labeled_matrix
from utils.generate_initial_score import generate_judge_score_matrix


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

    except Exception as e:
        print(f"Error: {e}. Ensure JSON files are formatted correctly.")