CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the table (Postgres now knows what 'vector' means)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    age INTEGER,
    current_traits TEXT[] DEFAULT '{}', 
    profile_summary TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);