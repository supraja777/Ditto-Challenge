CREATE TABLE IF NOT EXISTS matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- IDs linking back to the users table
    user_a_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Match Metadata
    intent TEXT, -- e.g., 'Networking', 'Friendship', 'Collaboration'
    compatibility FLOAT, -- The final_score (0.0 to 1.0)
    
    -- Feedback Loop
    feedback_text TEXT DEFAULT '', -- Raw text from the user
    is_processed BOOLEAN DEFAULT FALSE, -- Flag for Thursday's FeedbackAgent
    
    -- Temporal Data
    match_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraint: Prevent duplicate pairings in the same run
    CONSTRAINT unique_match_pair UNIQUE (user_a_id, user_b_id, match_date)
);