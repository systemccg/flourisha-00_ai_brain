-- Add vector embedding support to processed_content table
-- Requires pgvector extension (already enabled in Supabase)

-- Add embedding column (1536 dimensions for text-embedding-3-small)
ALTER TABLE processed_content
ADD COLUMN IF NOT EXISTS embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model text,
ADD COLUMN IF NOT EXISTS embedding_text text;

-- Create index for vector similarity search (IVFFlat)
CREATE INDEX IF NOT EXISTS processed_content_embedding_idx
ON processed_content
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: HNSW index (better for accuracy, slightly slower writes)
-- CREATE INDEX IF NOT EXISTS processed_content_embedding_hnsw_idx
-- ON processed_content
-- USING hnsw (embedding vector_cosine_ops);

-- Create search function for vector similarity
CREATE OR REPLACE FUNCTION search_content_by_embedding(
    query_embedding vector(1536),
    match_tenant_id text,
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id text,
    title text,
    content_type text,
    summary text,
    tags text[],
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pc.id,
        pc.title,
        pc.content_type,
        pc.summary,
        pc.tags,
        1 - (pc.embedding <=> query_embedding) as similarity
    FROM processed_content pc
    WHERE pc.tenant_id = match_tenant_id
        AND pc.embedding IS NOT NULL
        AND 1 - (pc.embedding <=> query_embedding) > match_threshold
    ORDER BY pc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION search_content_by_embedding TO authenticated;

-- Comments
COMMENT ON COLUMN processed_content.embedding IS 'Vector embedding for semantic search (OpenAI text-embedding-3-small)';
COMMENT ON COLUMN processed_content.embedding_model IS 'Model used to generate embedding';
COMMENT ON COLUMN processed_content.embedding_text IS 'Text used to generate embedding (first 1000 chars)';
