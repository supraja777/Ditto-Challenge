import pandas as pd
import os
import numpy as np
from scipy.optimize import linear_sum_assignment
from app_logging import setup_matchmaking_loggers

# Load Loggers
system_log, ai_log = setup_matchmaking_loggers()

def generate_optimized_pairs(file_name="matches_score_matrix.csv"):
    file_path = os.path.join("outputs", file_name)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        # Load the matrix
        df = pd.read_csv(file_path, index_col=0)
        
        # The Hungarian Algorithm minimizes cost, so we must subtract 
        # our scores from a large number to maximize the "profit" (compatibility).
        cost_matrix = 1 - df.values
        
        # 1. SOLVE: Linear Sum Assignment
        # row_ind represents UserA index, col_ind represents UserB index
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        print("\n" + "═"*60)
        print(f"║ {'OPTIMIZED WEEKLY MATCHES (MAXIMIZED VOLUME)':^56} ║")
        print("═"*60)
        print(f"{'User A':<15} | {'User B':<15} | {'Confidence Score':<15}")
        print("-" * 60)

        seen_pairs = set()
        final_pairs = []

        for i, j in zip(row_ind, col_ind):
            # Ensure we don't match someone with themselves 
            # and don't print the same pair twice (A-B and B-A)
            if i != j:
                pair = tuple(sorted((df.index[i], df.index[j])))
                if pair not in seen_pairs:
                    score = df.iloc[i, j]
                    print(f"{pair[0]:<15} | {pair[1]:<15} | {score:<15.4f}")
                    seen_pairs.add(pair)
                    final_pairs.append({
                        "user_a": pair[0],
                        "user_b": pair[1],
                        "confidence_score": float(score)
                    })

        print("═"*60)
        
        # Step 6: Log the final decision to System Logs
        system_log.info(f"Final pairings generated for {len(final_pairs)} couples.")
        
        return final_pairs

    except Exception as e:
        system_log.error(f"Error in optimization: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_optimized_pairs()