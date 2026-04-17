-- 1. Create the Matches table
CREATE TABLE matches (
  -- Unique ID for the match
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- The User IDs (Using TEXT here if you are using custom strings/names from your JSON, 
  -- or UUID if you are linking to Supabase Auth)
  user_a_id TEXT NOT NULL,
  user_b_id TEXT NOT NULL,
  
  -- Match Status (Wednesday Protocol)
  accepted BOOLEAN DEFAULT FALSE,
  
  -- Numerical Data (Tuesday Protocol)
  confidence_score DECIMAL(5,4), -- Stores scores like 0.8925
  
  -- Feedback Data (Thursday Protocol)
  -- feedback_for_a: What User B said about User A
  -- feedback_for_b: What User A said about User B
  feedback_for_a TEXT,
  feedback_for_b TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ensure a user can't be matched with themselves
  CONSTRAINT no_self_match CHECK (user_a_id <> user_b_id)
);

-- 2. Enable Realtime (Optional: lets your dashboard update live)
ALTER PUBLICATION supabase_realtime ADD TABLE matches;