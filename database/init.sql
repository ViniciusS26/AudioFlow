CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS audios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_name TEXT NOT NULL,
    original_ext TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    duration_sec DOUBLE PRECISION,
    sample_rate INTEGER,
    channels INTEGER,
    bitrate INTEGER,
    processing_type TEXT NOT NULL DEFAULT 'original',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    path_original TEXT NOT NULL,
    path_processed TEXT
);

CREATE INDEX IF NOT EXISTS idx_audios_created_at ON audios (created_at DESC);
