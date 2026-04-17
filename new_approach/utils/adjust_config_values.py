import json
import os

from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Name your variable 'supabase_client' or 'db' instead of 'supabase'
supabase_client = create_client(url, key)

CONFIG_PATH = "config.json"

def updating_config_values(total_matches, successful_matches, target_matches=5):
    """
    Adjusts matchmaking parameters based on performance metrics.
    
    Args:
        total_matches (int): Total pairings generated.
        successful_matches (int): Count of matches where 'accepted' is True.
        target_matches (int): The desired volume of matches.
    """
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Error: {CONFIG_PATH} not found.")
        return

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # 1. Calculate Metrics
    unsuccessful_matches = total_matches - successful_matches
    success_rate = successful_matches / total_matches if total_matches > 0 else 0
    volume_ratio = total_matches / target_matches if target_matches > 0 else 1

    print(f"📊 Analyzing Metrics: Success Rate: {success_rate:.2f}, Volume Ratio: {volume_ratio:.2f}")

    # 2. Logic: Adjust Threshold based on Volume
    # If we aren't meeting the target volume, lower the entry bar.
    if volume_ratio < 1.0:
        config['matching_logic']['threshold'] = max(0.4, config['matching_logic']['threshold'] - 0.05)
        config['constraints']['penalty_for_intent_mismatch'] = max(0.1, config['constraints']['penalty_for_intent_mismatch'] - 0.05)
    elif volume_ratio > 1.2:
        # If we have too many matches, make the criteria stricter
        config['matching_logic']['threshold'] = min(0.9, config['matching_logic']['threshold'] + 0.02)

    # 3. Logic: Adjust Weights based on Quality (Success Rate)
    # If users aren't liking each other, increase the weight of personality embeddings
    if success_rate < 0.5 and total_matches > 0:
        config['weights']['personality_embedding_w'] = min(0.5, config['weights']['personality_embedding_w'] + 0.05)
        config['weights']['traits_embedding_w'] = min(0.4, config['weights']['traits_embedding_w'] + 0.05)
        
        # Reduce the weight of "hard" facts like age if quality is poor
        config['weights']['age_w'] = max(0.05, config['weights']['age_w'] - 0.02)
        
        # Reduce bias to stop "over-inflation" of scores
        config['embedding_config']['bias'] = max(0.0, config['embedding_config']['bias'] - 0.01)

    # 4. Balancing w_normal vs w_judge
    # If AI date simulations (judge) aren't predicting success well, rely more on math (normal)
    if success_rate < 0.4:
        config['weights']['w_normal'] = min(0.8, config['weights']['w_normal'] + 0.1)
        config['weights']['w_judge'] = max(0.2, 1.0 - config['weights']['w_normal'])

    # 5. Save the updated configuration
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Config updated and saved successfully.")
    except Exception as e:
        print(f"❌ Failed to save config: {e}")

    return config

def get_matchmaking_metrics():
    """
    Fetches the total number of matches and the number of successful matches
    from the Supabase 'matches' table.
    """
    try:
        # 1. Fetch all records from the matches table
        # We only need the 'accepted' column to calculate metrics
        response = supabase_client.table("matches").select("accepted").execute()

        
        
        if not response.data:
            print("⚠️ No match data found in database.")
            return 0, 0

        # 2. Calculate totals
        data = response.data
        total_matches = len(data)
        successful_matches = sum(1 for record in data if record.get('accepted') is True)

        print(f"📊 Metrics Fetched: Total={total_matches}, Successful={successful_matches}")
        return total_matches, successful_matches

    except Exception as e:
        print(f"❌ Error fetching matchmaking metrics: {e}")
        return 0, 0


