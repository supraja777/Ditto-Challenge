-- 1. Create the system_config table
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Populate with Initial "Rich Computation" Thresholds
INSERT INTO system_config (key, value, description) VALUES
('cosine_threshold', '0.5', 'Minimum similarity score required to be considered a match'),
('exploration_rate', '0.1', 'The epsilon value for the Explore vs. Exploit logic'),
('weight_vibe', '0.40', 'Weight for the Profile Summary (vibe) embedding'),
('weight_traits', '0.15', 'Weight for the Trait-specific embedding'),
('weight_intellect', '0.15', 'Weight for the Intellectual Focus similarity'),
('weight_age', '0.10', 'Weight for the Age Alignment score'),
('social_energy_bonus', '0.05', 'Bonus added for ideal social energy gaps'),
('hobby_bonus_unit', '0.02', 'Bonus added per shared hobby (capped at 0.10)');

-- 3. Create a trigger to auto-update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_config_timestamp BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();