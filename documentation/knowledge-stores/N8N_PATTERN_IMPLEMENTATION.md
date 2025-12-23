# n8n RAG Pattern - Implementation Status

**Date**: 2025-11-22
**Status**: ✅ Fully Aligned with n8n Pattern
**Reference**: `docs/N8N_TO_FLOURISHA_MAPPING.md`

---

## Three-Table Architecture (n8n Pattern)

### 1. document_metadata
**Purpose**: High-level document tracking with version control
**Status**: ✅ EXISTS in Supabase

**Schema**:
```sql
- id (file_id - video_id, etc.)
- title
- url
- content_hash (SHA-256 for version control)
- tenant_id, user_id, created_by
- version_number, is_current
- is_deleted, deleted_at, deleted_by
- document_type ('youtube_video', etc.)
- processing_status
- created_at, updated_at
```

**Service**: `services/document_metadata.py` ✅ CREATED
- `create_or_update_document()` - Version control with content hashing
- `get_document()` - Retrieve current version
- `soft_delete_document()` - Soft delete pattern
- `list_documents()` - List with tenant filtering

### 2. documents_pg
**Purpose**: Chunks with vector embeddings
**Status**: ✅ EXISTS in Supabase

**Schema**:
```sql
- id
- content (chunk text)
- text (duplicate for compatibility)
- embedding vector(1536)
- metadata jsonb (file_id, file_title, chunk_index, etc.)
- tenant_id, user_id, created_by
- version_number, is_current
- is_deleted, deleted_at, deleted_by
```

**Service**: `services/embeddings.py` ✅ UPDATED
- `store_chunks_with_embeddings()` - Batch insert chunks
- `search_similar_content()` - Vector similarity search
- Uses existing `match_documents` RPC function

### 3. document_rows
**Purpose**: Tabular data (CSV/Excel)
**Status**: ✅ EXISTS in Supabase
**Usage**: Not needed for YouTube videos (n/a)

---

## Processing Pipeline (n8n Pattern)

### YouTube Video Processing Flow

```
1. FETCH
   └─ YouTube API: metadata + transcript

2. VERSION CHECK (n8n pattern)
   ├─ Calculate SHA-256 hash of transcript
   ├─ Check document_metadata for existing hash
   └─ Skip if unchanged / create new version if changed

3. AI PROCESSING
   └─ Pydantic AI: summary, insights, actions, tags

4. STORE METADATA
   └─ document_metadata table
      • file_id: video_id
      • title, url, content_hash
      • tenant_id, user_id
      • version_number, is_current
      • document_type: 'youtube_video'

5. AGENTIC CHUNKING (n8n pattern)
   └─ Claude semantic splitting
      • Min: 400 chars
      • Max: 1000 chars
      • Respects semantic boundaries
      • Merges small chunks

6. EMBEDDINGS (n8n pattern)
   └─ OpenAI text-embedding-3-small
      • Batch generation (100/request)
      • 1536 dimensions

7. STORE CHUNKS
   └─ documents_pg table
      • content: chunk text
      • embedding: vector(1536)
      • metadata: {file_id, file_title, chunk_index, ...}
      • tenant_id for isolation

8. KNOWLEDGE GRAPH
   └─ Neo4j + Graphiti
      • add_episode() with full transcript
      • Automatic entity extraction

9. FILE STORAGE (Flourisha addition)
   └─ PARA structure
      • Markdown files
      • Google Drive sync
```

---

## Services Implemented

### ✅ services/document_metadata.py (NEW)
- Manages `document_metadata` table
- Version control with content hashing
- Soft delete pattern
- Tenant isolation

### ✅ services/embeddings.py (UPDATED)
- Uses `documents_pg` table
- Batch embedding generation
- Vector similarity search via `match_documents`
- Chunk storage with metadata

### ✅ services/chunking.py (NEW)
- Agentic chunking with Claude
- 400-1000 char semantic chunks
- Fallback to paragraph-based chunking
- Follows n8n LangChain pattern

### ✅ services/knowledge_graph.py (EXISTING)
- Neo4j + Graphiti integration
- Episodic memory storage
- Semantic search

### ✅ services/file_storage.py (EXISTING)
- PARA file organization
- Markdown generation
- Google Drive sync ready

---

## Key Patterns from n8n

### 1. Version Control ✅
```python
# Calculate content hash
content_hash = hashlib.sha256(transcript.encode()).hexdigest()

# Check if changed
existing = get_document(video_id, tenant_id)
if existing and existing['content_hash'] == content_hash:
    return  # Skip - unchanged

# Mark old version as not current
update_document(video_id, is_current=False, superseded_at=now())

# Create new version
create_document(version_number=existing.version_number + 1)
```

### 2. Soft Delete ✅
```python
# Never hard delete - mark as deleted
soft_delete_document(file_id, tenant_id, deleted_by=user_id)
# Sets: is_deleted=True, deleted_at=now(), deleted_by=user_id

# Also soft delete chunks
soft_delete_chunks(file_id, tenant_id, deleted_by)
```

### 3. Multi-Tenant Isolation ✅
```python
# Every query includes tenant_id
query.eq('tenant_id', tenant_id).eq('is_deleted', False)

# Chunks link to parent via metadata
chunk_metadata = {
    'file_id': video_id,
    'file_title': title,
    'tenant_id': tenant_id
}
```

### 4. Agentic Chunking ✅
```python
# Claude determines semantic split points
chunker = get_chunker(max_chunk_size=1000, min_chunk_size=400)
chunks = await chunker.chunk(transcript)
# Returns semantically coherent chunks
```

### 5. Batch Embeddings ✅
```python
# Generate embeddings in batch (up to 100)
embeddings = await generate_embeddings_batch(chunks)
# Much faster than one-by-one
```

---

## Integration Points

### YouTube Router (`routers/youtube.py`)
**Line 271-342**: Full n8n pattern implementation
```python
1. Calculate content_hash
2. Create/update document_metadata
3. Agentic chunking (Claude)
4. Batch embeddings (OpenAI)
5. Store in documents_pg
6. Store in Neo4j (Graphiti)
7. Save PARA markdown file
```

### Background Worker (`workers/queue_worker.py`)
**Line 125-250**: Same pipeline for async processing

---

## What's Different from n8n

### ✅ Improvements
1. **Firebase JWT**: Proper signature verification (n8n only decodes)
2. **Pydantic AI**: Type-safe structured outputs (vs LangChain)
3. **Claude**: Better content analysis (vs GPT-4.1-mini)
4. **PARA Files**: Markdown + Google Drive sync (n8n doesn't have this)
5. **Projects**: Project-specific context/tech stack translation

### ✅ Kept from n8n
1. Three-table architecture (metadata + chunks + rows)
2. Version control with content hashing
3. Soft delete pattern
4. Agentic chunking (400-1000 chars)
5. OpenAI embeddings (text-embedding-3-small)
6. Multi-tenant isolation
7. Batch processing

### ❌ Not Implemented (Not Needed)
1. CSV/Excel processing (document_rows table exists but unused)
2. Google Drive polling (we use YouTube API)
3. MIME type detection (single content type: video)

---

## Testing

### Test document_metadata
```bash
cd backend
source venv/bin/activate
python -c "
from services.document_metadata import get_metadata_service
metadata = get_metadata_service()
# Test version control, soft delete, listing
"
```

### Test full pipeline
```bash
# Start backend
uvicorn main:app --reload

# Process video via API
POST /youtube/process/{video_id}

# Check all three storage layers:
# 1. document_metadata table (high-level)
# 2. documents_pg table (chunks with embeddings)
# 3. Neo4j (knowledge graph)
```

---

## Database Status

### ✅ Existing Tables (Verified)
- `document_metadata` - 1 row (from n8n workflow)
- `documents_pg` - 1 row (from n8n workflow)
- `document_rows` - 0 rows (exists, unused for videos)
- `processed_content` - 0 rows (Flourisha-specific, optional)
- `projects` - 0 rows (Flourisha-specific)
- `youtube_subscriptions` - 0 rows (Flourisha-specific)

### ✅ RPC Functions (Should Exist from n8n)
- `match_documents(query_embedding, tenant_id, threshold, count)` - Vector search
- Verify this exists in Supabase

---

## Next Steps

### 1. Verify RPC Function
Check if `match_documents` function exists:
```sql
SELECT routine_name
FROM information_schema.routines
WHERE routine_name = 'match_documents';
```

If missing, create it (from n8n pattern):
```sql
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_tenant_id text,
  match_threshold float DEFAULT 0.7,
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
    id,
    content,
    metadata,
    1 - (embedding <=> query_embedding) AS similarity
  FROM documents_pg
  WHERE tenant_id = match_tenant_id
    AND is_deleted = FALSE
    AND 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
```

### 2. Test End-to-End (After Auth Fixed)
1. Process YouTube video
2. Verify in document_metadata (1 row with video_id)
3. Verify in documents_pg (N rows with chunks)
4. Test vector search with match_documents
5. Check Neo4j for knowledge graph

### 3. Add Two-Stage Retrieval (n8n Pattern)
```python
# Stage 1: Vector search (top 25)
results = await embeddings.search_similar_content(query, tenant_id, limit=25)

# Stage 2: Cohere reranking (reduce to top 4)
reranked = cohere.rerank(query, results, top_n=4)
```

---

## Summary

✅ **Fully Aligned with n8n RAG Pattern**
- Three-table architecture implemented
- Version control with content hashing
- Soft delete pattern
- Agentic chunking (Claude)
- Batch embeddings (OpenAI)
- Multi-tenant isolation
- Knowledge graph (Graphiti)

🎯 **Ready For**:
- End-to-end video processing
- Vector similarity search
- Two-stage retrieval (vector + rerank)
- Multi-tool agent (future)

---

**Last Updated**: 2025-11-22
**Status**: Ready for testing once Firebase auth is fixed
