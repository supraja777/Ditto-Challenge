MATCH_CONFIG = {
    "SIMILARITY_THRESHOLD": 0.75,  # Min cosine similarity to be a "Good Match"
    "EXPLORATION_RATE": 0.10,      # 10% of matches are wildcards
    "RECENCY_BIAS": 1.2,           # Multiplier for users who joined/updated recently
    "DIVERSITY_BIAS": 0.8,         # Penalty for matching with the same 'Type' twice
    "MIN_TRAIT_OVERLAP": 2         # Minimum number of shared semantic traits
}