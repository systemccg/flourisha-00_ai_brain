# Knowledge Ingestion Service

Orchestrates document processing and ingestion into all three knowledge stores (Vector, Graph, Whole).

## Location

`/root/flourisha/00_AI_Brain/services/knowledge_ingestion_service.py`

## Overview

The `KnowledgeIngestionService` is the main entry point for adding documents to the AI Brain. It:
1. Extracts content using pluggable backends
2. Validates extraction accuracy
3. Stores in all three knowledge stores
4. Provides unified query interface

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     ingest_document()                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: EXTRACT                                             │
│  DocumentProcessor.extract_with_backend()                    │
│  • Uses Claude (primary) or Docling (fallback)              │
│  • Extracts text, entities, relationships                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: VALIDATE                                            │
│  • Check for hallucinations                                  │
│  • Verify entity names appear in source                     │
│  • Set confidence levels                                    │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  WHOLE STORE    │   │  GRAPH STORE    │   │  VECTOR STORE   │
│                 │   │                 │   │                 │
│ _store_raw_     │   │ _store_in_      │   │ _store_in_      │
│  document()     │   │  graph()        │   │  vector()       │
│                 │   │                 │   │                 │
│ • Raw text      │   │ • Entities      │   │ • Chunk text    │
│ • Markdown      │   │ • Relations     │   │ • Embed chunks  │
│ • Metadata      │   │ • Episode       │   │ • Store vectors │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## Usage Examples

### Simple Ingestion
```python
from services.knowledge_ingestion_service import ingest_document

result = await ingest_document(
    file_path="/path/to/document.pdf",
    document_type="medical",
    tenant_id="default"
)

print(f"Document ID: {result['document_id']}")
print(f"Entities: {result['entities_extracted']}")
print(f"Chunks: {result['chunks_created']}")
```

### Full Control
```python
from services.knowledge_ingestion_service import get_ingestion_service
from services.document_processor import ExtractionBackendType

service = get_ingestion_service(
    tenant_id="my_tenant",
    extraction_backend=ExtractionBackendType.CLAUDE
)

result = await service.ingest_document(
    file_path="/path/to/document.pdf",
    document_type="legal",
    metadata={"source": "contract", "client": "ACME"},
    extract_entities=True,
    entity_types=["person", "organization", "date", "money"],
    store_in_vector=True,
    store_in_graph=True,
    store_raw=True
)
```

### Selective Storage
```python
# Store only in vector (for semantic search only)
result = await service.ingest_document(
    file_path="/path/to/document.pdf",
    store_in_vector=True,
    store_in_graph=False,
    store_raw=False
)
```

## Query Interface

### Combined Query
```python
results = await service.query_knowledge(
    query="blood pressure medications",
    search_vector=True,
    search_graph=True,
    limit=10
)

# Vector results (semantic similarity)
for r in results["vector_results"]:
    print(f"Chunk: {r['content'][:100]}...")
    print(f"Similarity: {r['similarity']}")

# Graph results (relationships)
for r in results["graph_results"]:
    print(f"Entity: {r['name']}")
    print(f"Related: {r['relationships']}")
```

## Ingestion Result

```python
{
    "status": "success",  # or "partial", "failed"
    "file_path": "/path/to/document.pdf",
    "document_id": "doc_abc123def456",
    "stores": {
        "raw": {"status": "success", "stored_bytes": 15420},
        "graph": {"status": "success", "entities_stored": 12, "relationships_stored": 8},
        "vector": {"status": "success", "chunks_stored": 24, "total_characters": 45000}
    },
    "entities_extracted": 12,
    "relationships_extracted": 8,
    "chunks_created": 24,
    "warnings": [],
    "errors": [],
    "duration_seconds": 3.45
}
```

## Multi-Tenant Support

The service supports multi-tenant isolation via `tenant_id`:

```python
# Tenant A's documents
service_a = get_ingestion_service(tenant_id="tenant_a")
await service_a.ingest_document(...)

# Tenant B's documents
service_b = get_ingestion_service(tenant_id="tenant_b")
await service_b.ingest_document(...)

# Queries are automatically filtered by tenant
results = await service_a.query_knowledge("search term")
# Returns only tenant_a's documents
```

## Document ID Generation

Document IDs are generated from file content hash:
```python
file_hash = hashlib.sha256(file_content).hexdigest()[:16]
document_id = f"doc_{file_hash}"
```

This ensures:
- Same document → same ID (deduplication)
- Different documents → different IDs
- Deterministic and reproducible

## Error Handling

```python
result = await service.ingest_document(file_path)

if result["status"] == "failed":
    print(f"Errors: {result['errors']}")
elif result["status"] == "partial":
    print(f"Warnings: {result['warnings']}")
    # Some stores may have failed
    for store, info in result["stores"].items():
        if info.get("status") == "failed":
            print(f"{store} failed: {info['error']}")
```

## Configuration

### Environment Variables
```bash
# Claude backend
ANTHROPIC_API_KEY=sk-...

# Docling backend
DOCLING_API_URL=https://docling.leadingai.info

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
```

### Chunking Settings
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters

## YouTube Video Ingestion

For YouTube videos, use the `TranscriptService` to extract transcripts before ingestion:

```python
from services.transcript_service import get_transcript
from services.knowledge_ingestion_service import ingest_document
import tempfile

# Step 1: Get transcript (uses Tor proxy → Whisper fallback)
result = get_transcript("VIDEO_ID")

if result.success:
    # Step 2: Save transcript to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(result.transcript)
        temp_path = f.name

    # Step 3: Ingest into AI Brain
    ingestion_result = await ingest_document(
        file_path=temp_path,
        document_type="youtube_video",
        metadata={
            "video_id": result.video_id,
            "source": result.source.value,
            "language": result.language,
            "url": f"https://youtube.com/watch?v={result.video_id}"
        }
    )
```

### YouTube Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  YouTube Video URL                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TranscriptService (Tier 1: Tor Proxy)                       │
│  youtube-transcript-api via socks5://127.0.0.1:9050         │
└─────────────────────────────────────────────────────────────┘
                              │
                     (if failed)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TranscriptService (Tier 2: Whisper Fallback)               │
│  yt-dlp audio download + faster-whisper transcription        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ContentProcessorAgent (AI Analysis)                         │
│  • Summary generation                                        │
│  • Key insights extraction                                   │
│  • Action items                                              │
│  • Tags and relevance scoring                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  KnowledgeIngestionService                                   │
│  → Vector Store (searchable chunks)                         │
│  → Graph Store (entities & relationships)                   │
│  → Whole Store (full transcript)                            │
│  → PARA File (markdown in Resources)                        │
└─────────────────────────────────────────────────────────────┘
```

### Requirements for YouTube Ingestion

1. **Tor proxy running** on port 9050 (see [TOR_PROXY_SETUP.md](../infrastructure/TOR_PROXY_SETUP.md))
2. **faster-whisper** installed for fallback transcription
3. **yt-dlp** and **ffmpeg** for audio download

```bash
# Verify requirements
systemctl status tor
ss -tlnp | grep 9050
python3 -c "from faster_whisper import WhisperModel; print('OK')"
which yt-dlp ffmpeg
```

## Related Documentation

- [Transcript Service](./TRANSCRIPT_SERVICE.md) - YouTube transcript extraction with Tor/Whisper
- [Tor Proxy Setup](../infrastructure/TOR_PROXY_SETUP.md) - Tor installation and configuration
- [Document Processor](./DOCUMENT_PROCESSOR.md) - Extraction details
- [Extraction Backends](./EXTRACTION_BACKENDS.md) - Backend comparison
- [Knowledge Stores Overview](../knowledge-stores/OVERVIEW.md) - Three-store architecture
- [Database Schema](../database/DATABASE_SCHEMA.md) - Table structures

---

*Last updated: 2025-12-14*

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
