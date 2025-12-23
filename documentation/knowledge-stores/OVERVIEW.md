# Knowledge Stores Overview

The AI Brain uses a three-store architecture for comprehensive knowledge management.

## The Three Stores

| Store | Technology | Purpose | Best For |
|-------|------------|---------|----------|
| **Vector** | Supabase pgvector | Semantic similarity search | "Find similar content" |
| **Graph** | Neo4j/Graphiti | Entities & relationships | "How are things connected?" |
| **Whole** | Supabase (raw) | Original documents | "Show me the source" |

## Architecture Diagram

```
                    ┌─────────────────┐
                    │    Document     │
                    │   (PDF, etc.)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Extraction    │
                    │   (Claude or    │
                    │    Docling)     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  VECTOR STORE   │ │  GRAPH STORE    │ │  WHOLE STORE    │
│                 │ │                 │ │                 │
│  • Chunks       │ │  • Entities     │ │  • Raw text     │
│  • Embeddings   │ │  • Relations    │ │  • Markdown     │
│  • Similarity   │ │  • Episodes     │ │  • Metadata     │
│                 │ │                 │ │                 │
│  Supabase       │ │  Neo4j          │ │  Supabase       │
│  pgvector       │ │  Graphiti       │ │  documents      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Query       │
                    │   (Combined)    │
                    └─────────────────┘
```

## When to Use Each Store

### Vector Store (Semantic Search)
Use when you need to find content by meaning, not exact keywords.

**Examples:**
- "Find documents about blood pressure management"
- "What have I learned about project planning?"
- "Documents similar to this one"

**How it works:**
1. Text is split into chunks (~1000 chars)
2. Each chunk gets an embedding vector
3. Queries are also embedded
4. Cosine similarity finds matches

### Graph Store (Relationships)
Use when you need to understand connections between entities.

**Examples:**
- "What medications interact with aspirin?"
- "Who is connected to this project?"
- "What symptoms are associated with this condition?"

**How it works:**
1. Entities extracted (people, medications, conditions)
2. Relationships mapped (PRESCRIBED, TREATS, CONNECTED_TO)
3. Graph queries traverse connections

### Whole Store (Source Reference)
Use when you need the original, unprocessed content.

**Examples:**
- "Show me the original PDF"
- "What exactly did the document say?"
- "Verify this extracted information"

**How it works:**
1. Original text and markdown stored
2. Full document retained
3. Direct lookup by document ID

## Data Flow

```
1. INGEST
   File → DocumentProcessor → ExtractionResult

2. STORE
   ExtractionResult → KnowledgeIngestionService
                    ├→ _store_raw_document()     → Whole Store
                    ├→ _store_in_graph()         → Graph Store
                    └→ _store_in_vector()        → Vector Store

3. QUERY
   Query → query_knowledge()
         ├→ Vector search (semantic)
         └→ Graph search (relationships)

4. COMBINE
   Results merged and ranked
```

## Query Examples

### Combined Query
```python
from services.knowledge_ingestion_service import get_ingestion_service

service = get_ingestion_service()
results = await service.query_knowledge(
    query="blood pressure medications",
    search_vector=True,
    search_graph=True,
    limit=10
)

# results["vector_results"] - semantic matches
# results["graph_results"] - relationship matches
```

### Vector Only
```python
results = await service.query_knowledge(
    query="project management techniques",
    search_vector=True,
    search_graph=False
)
```

## Related Documentation

- [Vector Store Details](./VECTOR_STORE.md) (in database/)
- [Graph Store Details](./GRAPH_STORE.md)
- [Knowledge Ingestion Service](../services/KNOWLEDGE_INGESTION.md)
- [Extraction Backends](../services/EXTRACTION_BACKENDS.md)

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
