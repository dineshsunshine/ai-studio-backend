-- Migration: Add generate_audio column to video_jobs table
-- Date: 2025-10-31

-- For SQLite (local dev)
ALTER TABLE video_jobs ADD COLUMN generate_audio BOOLEAN DEFAULT 0;

-- For PostgreSQL (production)
-- ALTER TABLE video_jobs ADD COLUMN generate_audio BOOLEAN DEFAULT FALSE;

