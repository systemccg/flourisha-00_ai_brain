# Vector Store

pgvector-based semantic search in Supabase PostgreSQL.

## Overview

The vector store enables semantic similarity search using OpenAI embeddings stored in PostgreSQL with the pgvector extension.

## Configuration

| Setting | Value |
|---------|-------|
| **Database** | Supabase PostgreSQL |
| **Extension** | pgvector |
| **Embedding Model** | text-embedding-3-small |
| **Dimensions** | 1536 |
| **Index Type** | IVFFlat (cosine similarity) |

## Schema

### Embedding Columns on processed_content

```sql
-- Added via 02_add_embeddings.sql
ALTER TABLE processed_content
ADD COLUMN embedding vector(1536),
ADD COLUMN embedding_model text,
ADD COLUMN embedding_text text;
```

| Column | Type | Description |
|--------|------|-------------|
| `embedding` | vector(1536) | The embedding vector |
| `embedding_model` | text | Model used (e.g., "text-embedding-3-small") |
| `embedding_text` | text | Source text used for embedding |

### Index

```sql
-- IVFFlat index for cosine similarity
CREATE INDEX processed_content_embedding_idx
ON processed_content
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## Search Function

### SQL Function
```sql
CREATE FUNCTION search_content_by_embedding(
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
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query_embedding` | vector(1536) | required | Query embedding vector |
| `match_tenant_id` | text | required | Tenant for filtering |
| `match_threshold` | float | 0.7 | Minimum similarity (0-1) |
| `match_count` | int | 10 | Maximum results |

### Usage

```sql
SELECT * FROM search_content_by_embedding(
    '[0.1, 0.2, ...]'::vector(1536),
    'default',
    0.7,
    10
);
```

## Python Integration

### Generate Embedding
```python
from services.embeddings_service import get_embeddings

embeddings = get_embeddings()
vector = await embeddings.embed("search query text")
```

### Search
```python
from services.supabase_client import get_supabase_client

supabase = await get_supabase_client()

results = supabase.rpc(
    "search_content_by_embedding",
    {
        "query_embedding": vector,
        "match_tenant_id": "default",
        "match_threshold": 0.7,
        "match_count": 10
    }
).execute()

for item in results.data:
    print(f"{item['title']}: {item['similarity']:.2f}")
```

### Via Ingestion Service
```python
from services.knowledge_ingestion_service import get_ingestion_service

service = get_ingestion_service()
results = await service.query_knowledge(
    query="blood pressure medications",
    search_vector=True,
    search_graph=False,
    limit=10
)

for r in results["vector_results"]:
    print(f"{r['title']}: {r['similarity']}")
```

## Embedding Models

### Current: text-embedding-3-small
- **Dimensions**: 1536
- **Cost**: ~$0.00002 per 1K tokens
- **Quality**: Good for most use cases

### Alternative: text-embedding-3-large
- **Dimensions**: 3072
- **Cost**: ~$0.00013 per 1K tokens
- **Quality**: Better for nuanced similarity

To switch models, update:
1. `embeddings_service.py` - model name
2. SQL schema - vector dimensions
3. Re-embed all content

## Chunking Strategy

Content is chunked before embedding:

| Setting | Value |
|---------|-------|
| **Chunk size** | 1000 characters |
| **Chunk overlap** | 200 characters |
| **Separator** | Sentence boundaries when possible |

### Chunk Storage

```
document_chunks table:
- id: "{document_id}_chunk_{index}"
- document_id: Reference to parent
- chunk_index: Position in document
- content: Chunk text
- embedding: Chunk embedding
```

## Performance Tuning

### Index Selection

| Index Type | Pros | Cons | Use When |
|------------|------|------|----------|
| **IVFFlat** | Faster writes, good recall | Needs tuning | < 1M vectors |
| **HNSW** | Better accuracy | Slower writes | > 1M vectors |

### IVFFlat Tuning
```sql
-- lists = sqrt(n) for n vectors, min 100
WITH (lists = 100)  -- Good for < 10K vectors
WITH (lists = 316)  -- Good for ~100K vectors
```

### Query Tuning
```sql
-- Increase probes for better accuracy
SET ivfflat.probes = 10;  -- Default is 1
```

## Similarity Metrics

pgvector supports:

| Metric | Operator | Description |
|--------|----------|-------------|
| Cosine | `<=>` | Best for text (default) |
| L2 (Euclidean) | `<->` | Distance-based |
| Inner Product | `<#>` | Dot product |

### Cosine Similarity Formula
```
similarity = 1 - (embedding <=> query_embedding)
```

Range: 0 (different) to 1 (identical)

## Troubleshooting

### No Results
1. Check threshold - lower from 0.7 to 0.5
2. Verify embeddings exist: `SELECT COUNT(*) FROM processed_content WHERE embedding IS NOT NULL`
3. Check tenant_id filter

### Slow Queries
1. Check index exists: `\di processed_content_embedding_idx`
2. Increase probes: `SET ivfflat.probes = 10`
3. Consider HNSW for large datasets

### Dimension Mismatch
```
Error: different vector dimensions
```
- Query vector must be 1536 dimensions
- Check embedding model matches schema

## Related Documentation

- [Database Schema](./DATABASE_SCHEMA.md) - Full schema reference
- [Knowledge Stores Overview](../knowledge-stores/OVERVIEW.md) - Three-store architecture
- [Knowledge Ingestion](../services/KNOWLEDGE_INGESTION.md) - Ingestion pipeline

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
