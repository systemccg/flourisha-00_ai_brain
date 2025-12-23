# Graph Store

Neo4j-based knowledge graph using Graphiti for entity and relationship storage.

## Overview

The graph store captures entities (people, medications, organizations, etc.) and their relationships, enabling queries like "what medications interact with X" or "who is connected to this project."

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Database** | Neo4j |
| **Interface** | Graphiti (Python library) |
| **Schema** | Dynamic (schema-less) |

## Core Concepts

### Episodes
An episode represents a unit of knowledge from a source (document, conversation, etc.):

```python
await kg.add_episode(
    content_id="doc_abc123",
    tenant_id="default",
    title="Medical Summary Nov 2025",
    content="Full document text...",
    summary="Patient visit summary with medication changes",
    source_description="Document type: medical"
)
```

### Entities
Named things extracted from content:

| Type | Examples |
|------|----------|
| `medication` | Aspirin, Metformin, Lisinopril |
| `person` | Dr. Smith, John Doe |
| `condition` | Hypertension, Diabetes |
| `organization` | ACME Corp, Memorial Hospital |
| `date` | November 26, 2025 |

### Relationships
Connections between entities:

| Type | Example |
|------|---------|
| `PRESCRIBED` | Dr. Smith → PRESCRIBED → Aspirin |
| `TREATS` | Aspirin → TREATS → Headache |
| `STOPPED` | Patient → STOPPED → Chlorella |
| `WORKS_AT` | Dr. Smith → WORKS_AT → Memorial Hospital |

## Data Model

```
                    ┌─────────────────┐
                    │    Episode      │
                    │                 │
                    │  - content_id   │
                    │  - tenant_id    │
                    │  - title        │
                    │  - content      │
                    └────────┬────────┘
                             │
                    EXTRACTED_FROM
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     Entity      │ │     Entity      │ │     Entity      │
│   (Medication)  │ │    (Person)     │ │   (Condition)   │
│                 │ │                 │ │                 │
│  name: Aspirin  │ │ name: Dr.Smith  │ │name: Headache   │
└────────┬────────┘ └────────┬────────┘ └─────────────────┘
         │                   │
         └───PRESCRIBED──────┘
                 │
                 └─────────TREATS───────────────────┘
```

## Integration

### Via Knowledge Ingestion Service

```python
from services.knowledge_ingestion_service import get_ingestion_service

service = get_ingestion_service()

# Ingest document (auto-extracts to graph)
result = await service.ingest_document(
    file_path="/path/to/document.pdf",
    store_in_graph=True
)

print(f"Entities stored: {result['stores']['graph']['entities_stored']}")
print(f"Relationships: {result['stores']['graph']['relationships_stored']}")
```

### Direct Graph Access

```python
from services.knowledge_graph_service import get_knowledge_graph

kg = get_knowledge_graph()

# Add episode
await kg.add_episode(
    content_id="doc_123",
    tenant_id="default",
    title="Meeting Notes",
    content="John discussed the project with Sarah..."
)

# Search
results = await kg.search_similar_content(
    query="project discussions",
    tenant_id="default",
    limit=10
)
```

## Query Examples

### Find Related Entities
```python
# What medications is this patient taking?
results = await kg.query("""
    MATCH (p:Person {name: 'John Doe'})-[:TAKES]->(m:Medication)
    RETURN m.name
""")
```

### Traverse Relationships
```python
# What conditions do these medications treat?
results = await kg.query("""
    MATCH (m:Medication)-[:TREATS]->(c:Condition)
    WHERE m.name IN ['Aspirin', 'Lisinopril']
    RETURN m.name, c.name
""")
```

### Find Connections
```python
# How are these two people connected?
results = await kg.query("""
    MATCH path = shortestPath(
        (a:Person {name: 'John'})-[*]-(b:Person {name: 'Sarah'})
    )
    RETURN path
""")
```

## Entity Extraction

### Via Claude Backend

The Claude extraction backend automatically extracts entities:

```python
from services.document_processor import get_document_processor, ExtractionBackendType

processor = await get_document_processor(
    default_backend=ExtractionBackendType.CLAUDE
)

result = await processor.extract_with_backend(
    file_path="/path/to/document.pdf",
    extract_entities=True,
    entity_types=["medication", "person", "condition", "date"]
)

for entity in result.entities:
    print(f"{entity.entity_type}: {entity.name}")
    if entity.value:
        print(f"  Value: {entity.value}")
```

### Via Graphiti (Auto-Extraction)

Graphiti can also auto-extract entities when adding episodes:

```python
# Graphiti extracts entities automatically from content
await kg.add_episode(
    content_id="doc_123",
    content="Dr. Smith prescribed Aspirin for John's headache."
    # Graphiti extracts: Dr. Smith (Person), Aspirin (Medication), John (Person), headache (Condition)
)
```

## Configuration

### Environment Variables
```bash
NEO4J_URI=bolt://neo4j.leadingai.info:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<password>
```

### Service Configuration
```python
from services.knowledge_graph_service import KnowledgeGraphService

kg = KnowledgeGraphService(
    uri="bolt://neo4j:7687",
    user="neo4j",
    password="secret"
)
```

## Multi-Tenant Support

All graph operations are filtered by `tenant_id`:

```python
# Tenant A's entities
await kg.add_episode(tenant_id="tenant_a", ...)

# Query only returns tenant_a's data
results = await kg.search_similar_content(
    tenant_id="tenant_a",
    query="..."
)
```

## Performance Considerations

### Indexing
Neo4j indexes are created automatically by Graphiti for:
- Entity names
- Tenant IDs
- Relationship types

### Query Optimization
- Use specific relationship types when possible
- Limit traversal depth for complex queries
- Use parameters instead of string concatenation

## Comparison with Vector Store

| Aspect | Graph Store | Vector Store |
|--------|-------------|--------------|
| **Query type** | Relationships, connections | Semantic similarity |
| **Best for** | "How are X and Y related?" | "Find content similar to X" |
| **Structure** | Entities + relationships | Flat chunks + embeddings |
| **Use case** | Knowledge graphs, reasoning | Search, retrieval |

## Related Documentation

- [Knowledge Stores Overview](./OVERVIEW.md) - Three-store architecture
- [Graphiti Integration](./GRAPHITI_INTEGRATION.md) - Detailed Graphiti setup
- [Extraction Backends](../services/EXTRACTION_BACKENDS.md) - Entity extraction
- [Vector Store](../database/VECTOR_STORE.md) - Semantic search

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
