# Database Documentation

Documentation for AI Brain database schemas and storage.

## Database Index

| Topic | File | Description |
|-------|------|-------------|
| Schema Overview | [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | All tables, SQL files |
| Vector Store | [VECTOR_STORE.md](./VECTOR_STORE.md) | pgvector embeddings |

## Database Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       Supabase                          │
│                    (PostgreSQL)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │    documents    │  │ document_chunks │              │
│  │   (raw text)    │  │  (embeddings)   │              │
│  └─────────────────┘  └─────────────────┘              │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │    episodes     │  │    entities     │              │
│  │  (Graphiti)     │  │  (extracted)    │              │
│  └─────────────────┘  └─────────────────┘              │
│                                                         │
│  Extension: pgvector (vector similarity search)         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## SQL Files Location

Schema definitions are in:
```
/root/flourisha/00_AI_Brain/database/
├── 01_content_intelligence_schema.sql  # Core tables
├── 02_add_embeddings.sql               # Vector support
└── ...
```

## Quick Queries

### Search by Embedding
```sql
SELECT * FROM match_document_chunks(
    query_embedding := '[...]'::vector,
    match_count := 10,
    filter_tenant := 'default'
);
```

### Get Document
```sql
SELECT * FROM documents WHERE id = 'doc_abc123';
```

### List Chunks
```sql
SELECT * FROM document_chunks
WHERE document_id = 'doc_abc123'
ORDER BY chunk_index;
```

## Related Documentation

- [Knowledge Stores Overview](../knowledge-stores/OVERVIEW.md)
- [Knowledge Ingestion Service](../services/KNOWLEDGE_INGESTION.md)

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
