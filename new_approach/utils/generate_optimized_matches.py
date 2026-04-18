import pandas as pd
import os
import numpy as np
from scipy.optimize import linear_sum_assignment

from db.matches_utility import upload_matches_to_supabase

def generate_optimized_pairs(file_name="matches_score_matrix.csv"):
    file_path = os.path.join("outputs", file_name)
    
    if not os.path.exists(file_path):
       print(f"File not found: {file_path}")
       return

    try:
        df = pd.read_csv(file_path, index_col=0)
        matrix_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(-1.0).values

        cost_matrix = 10 - matrix_numeric
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        print("\n" + "═"*60)
        print(f"║ {'OPTIMIZED WEEKLY MATCHES':^56} ║")
        print("═"*60)
        print(f"{'User A ID':<20} | {'User B ID':<20} | {'Score':<10}")
        print("-" * 60)

        seen_users = set()
        final_pairs = []

        for i, j in zip(row_ind, col_ind):   
            user_a_id = df.index[i]
            user_b_id = df.columns[j]
            score = matrix_numeric[i, j]

            if i != j and user_a_id not in seen_users and user_b_id not in seen_users:
                if score > -5:
                    print(f"{str(user_a_id)[:18]:<20} | {str(user_b_id)[:18]:<20} | {score:<10.3f}")
                    
                    final_pairs.append({
                        "user_a_id": user_a_id,
                        "user_b_id": user_b_id,
                        "confidence_score": float(score)
                    })
                    
                    seen_users.add(user_a_id)
                    seen_users.add(user_b_id)

        print("═"*60)
        
        if final_pairs:
            upload_matches_to_supabase(final_pairs)
        else:
            print("No valid matches found above the threshold.")

        return final_pairs

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_optimized_pairs()