import pandas as pd
import os
import numpy as np
from scipy.optimize import linear_sum_assignment

from db.matches_utility import upload_matches_to_supabase
# from app_logging import setup_matchmaking_loggers

# Load Loggers
# system_log, ai_log = setup_matchmaking_loggers()

def generate_optimized_pairs(file_name="matches_score_matrix.csv"):
    # Path handling - ensure it looks in the data or outputs folder
    file_path = os.path.join("outputs", file_name)
    
    if not os.path.exists(file_path):
       print(f"File not found: {file_path}")
       return

    try:
        # 1. LOAD: Handle the MultiIndex or Single ID index from the CSV
        # We use index_col=0 to ensure the User IDs are treated as row labels
        df = pd.read_csv(file_path, index_col=0)

        # 2. CLEAN: Ensure all matrix values are numeric
        # This prevents 'unsupported operand' errors if a string slipped into the CSV
        matrix_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(-1.0).values
        
        # 3. COST TRANSFORMATION: Hungarian algorithm minimizes cost.
        # To maximize compatibility, we subtract scores from a constant.
        # We use a large constant (like 10) to keep costs positive even with penalties.
        cost_matrix = 10 - matrix_numeric
        
        # 4. SOLVE: Linear Sum Assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        print("\n" + "═"*60)
        print(f"║ {'OPTIMIZED WEEKLY MATCHES':^56} ║")
        print("═"*60)
        print(f"{'User A ID':<20} | {'User B ID':<20} | {'Score':<10}")
        print("-" * 60)

        seen_users = set()
        final_pairs = []

        for i, j in zip(row_ind, col_ind):
            # Constraints:
            # 1. Don't match a user with themselves
            # 2. Don't match the same user twice in one week
            # 3. Score must be > -5 (avoiding the -10.0 deal-breaker threshold)
            
            user_a_id = df.index[i]
            user_b_id = df.columns[j]
            score = matrix_numeric[i, j]

            if i != j and user_a_id not in seen_users and user_b_id not in seen_users:
                if score > -5:  # Valid match threshold
                    print(f"{str(user_a_id)[:18]:<20} | {str(user_b_id)[:18]:<20} | {score:<10.3f}")
                    
                    final_pairs.append({
                        "user_a_id": user_a_id,
                        "user_b_id": user_b_id,
                        "confidence_score": float(score)
                    })
                    
                    # Mark both as 'busy' for this round
                    seen_users.add(user_a_id)
                    seen_users.add(user_b_id)

        print("═"*60)
        
        # 5. UPLOAD: Send UUIDs and scores to Supabase
        if final_pairs:
            upload_matches_to_supabase(final_pairs)
        else:
            print("No valid matches found above the threshold.")

        return final_pairs

    except Exception as e:
        #system_log.error(f"Error in optimization: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_optimized_pairs()