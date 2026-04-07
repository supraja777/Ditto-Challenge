-- 1. Enable the vector extension (Safe to run multiple times)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create or Update the table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Identity
    name TEXT NOT NULL,
    age INTEGER,
    traits TEXT[] DEFAULT '{}', 
    profile_summary TEXT,
    
    -- AI Vectors (Vibe vs. Specific Traits)
    -- Using 384 for local models (e.g., all-MiniLM-L6-v2) 
    -- Use 1536 if switching to OpenAI/Groq-compatible embeddings
    embedding vector(384),        -- Captures the broad 'profile_summary'
    trait_embedding vector(384),  -- Captures the specific 'current_traits' list
    
    -- Rich Computation Factors
    social_energy INTEGER DEFAULT 5,
    intent TEXT DEFAULT 'Exploring',
    intellectual_focus TEXT DEFAULT 'General',
    dealbreakers TEXT[] DEFAULT '{}',
    hobbies TEXT[] DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Optimization: High-Speed Similarity Indices
-- We index BOTH vectors so the database can handle dual-weighted searches instantly
CREATE INDEX ON users USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON users USING ivfflat (trait_embedding vector_cosine_ops) WITH (lists = 100);