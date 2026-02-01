-- Initialize PostgreSQL extensions required by Letta
-- This script runs automatically on first database creation

-- pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE NOTICE 'pgvector extension installed successfully';
    ELSE
        RAISE EXCEPTION 'pgvector extension failed to install';
    END IF;
END
$$;
