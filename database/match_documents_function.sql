-- Vector Similarity Search Function for documents_pg
-- Follows n8n RAG pattern for semantic search

CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_tenant_id text,
  match_threshold float DEFAULT 0.6,
  match_count int DEFAULT 25
)
RETURNS TABLE (
  id integer,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    documents_pg.id,
    documents_pg.content,
    documents_pg.metadata,
    1 - (documents_pg.embedding <=> query_embedding) AS similarity
  FROM documents_pg
  WHERE documents_pg.tenant_id = match_tenant_id
    AND documents_pg.is_deleted = FALSE
    AND documents_pg.is_current = TRUE
    AND 1 - (documents_pg.embedding <=> query_embedding) > match_threshold
  ORDER BY documents_pg.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents TO anon;
GRANT EXECUTE ON FUNCTION match_documents TO service_role;

-- Add comment
COMMENT ON FUNCTION match_documents IS 'Vector similarity search for documents_pg table using pgvector cosine distance. Returns top N matches above threshold.';
