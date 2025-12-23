# Services Documentation

Documentation for AI Brain services that process and manage knowledge.

## Services Index

| Service | File | Purpose |
|---------|------|---------|
| Document Processor | [DOCUMENT_PROCESSOR.md](./DOCUMENT_PROCESSOR.md) | Extract text from documents |
| Knowledge Ingestion | [KNOWLEDGE_INGESTION.md](./KNOWLEDGE_INGESTION.md) | Pipeline to all stores |
| Extraction Backends | [EXTRACTION_BACKENDS.md](./EXTRACTION_BACKENDS.md) | Claude, Docling, Legacy |

## Service Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   User / API Request                     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              KnowledgeIngestionService                   │
│         /services/knowledge_ingestion_service.py         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  DocumentProcessor                       │
│              /services/document_processor.py             │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ ClaudeBackend │   │DoclingBackend │   │ LegacyBackend │
│  (Primary)    │   │  (Fallback)   │   │  (Compat)     │
└───────────────┘   └───────────────┘   └───────────────┘
                            │
                            ▼
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Vector Store │   │  Graph Store  │   │  Whole Store  │
│  (pgvector)   │   │   (Neo4j)     │   │    (Raw)      │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Quick Reference

### Ingest a Document
```python
from services.knowledge_ingestion_service import ingest_document

result = await ingest_document(
    file_path="/path/to/document.pdf",
    document_type="medical",
    tenant_id="default"
)
```

### Process Without Storing
```python
from services.document_processor import process_file

text, metadata = await process_file(
    file_path="/path/to/document.pdf",
    use_new_backend=True,
    extract_entities=True
)
```

### Use Specific Backend
```python
from services.document_processor import get_document_processor, ExtractionBackendType

processor = await get_document_processor(
    default_backend=ExtractionBackendType.CLAUDE
)
result = await processor.extract_with_backend(file_path)
```

## Source Code Location

All services are in: `/root/flourisha/00_AI_Brain/services/`

```
services/
├── document_processor.py          # Main document processor
├── knowledge_ingestion_service.py # Ingestion orchestrator
├── extraction_backends/           # Pluggable backends
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   ├── claude_backend.py          # Claude extraction
│   └── docling_backend.py         # Docling extraction
├── knowledge_graph_service.py     # Neo4j/Graphiti
├── chunking_service.py            # Text chunking
├── embeddings_service.py          # Vector embeddings
└── supabase_client.py             # Database client
```

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
