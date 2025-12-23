# Extraction Backends

Pluggable document extraction backends for the AI Brain.

## Location

`/root/flourisha/00_AI_Brain/services/extraction_backends/`

```
extraction_backends/
├── __init__.py
├── base.py           # Abstract base class and data types
├── claude_backend.py # Claude API extraction
└── docling_backend.py # Docling API extraction
```

## Backend Comparison

| Feature | Claude | Docling | Legacy |
|---------|--------|---------|--------|
| **Accuracy** | Excellent | Good | Basic |
| **Complex layouts** | Excellent | Fair | Poor |
| **Entity extraction** | Built-in | Requires LLM | None |
| **Styled content** | Excellent | May miss | May miss |
| **Batch processing** | Sequential | Parallel | Sequential |
| **Cost** | API tokens | Free | Free |
| **Speed** | Moderate | Fast | Fast |

## Critical Warning

**Docling may miss styled content boxes.**

During testing with a medical document, Docling missed a "STOP CHLORELLA" instruction that was in a colored/styled box. Claude extracted it correctly.

**For medical or critical documents, always use Claude backend.**

## Data Types

### ExtractionResult
```python
@dataclass
class ExtractionResult:
    raw_text: str                    # Extracted text
    markdown: Optional[str]          # Formatted markdown
    entities: List[ExtractedEntity]  # Structured entities
    relationships: List[ExtractedRelationship]
    metadata: Dict[str, Any]
    backend_name: str                # "claude" or "docling"
    confidence: ExtractionConfidence
    validation_errors: List[str]
    validation_warnings: List[str]

    def is_valid(self) -> bool:
        return len(self.validation_errors) == 0
```

### ExtractedEntity
```python
@dataclass
class ExtractedEntity:
    name: str                        # Entity name/value
    entity_type: str                 # "medication", "person", etc.
    value: Optional[str]             # Associated value (dosage, etc.)
    confidence: ExtractionConfidence
    source_text: Optional[str]       # Original text location
    metadata: Dict[str, Any]
```

### ExtractedRelationship
```python
@dataclass
class ExtractedRelationship:
    source_entity: str
    target_entity: str
    relationship_type: str           # "PRESCRIBED", "TREATS", etc.
    properties: Dict[str, Any]
```

### ExtractionConfidence
```python
class ExtractionConfidence(Enum):
    HIGH = "high"       # Structured data, clear text
    MEDIUM = "medium"   # Some ambiguity
    LOW = "low"         # Uncertain, needs review
```

## Claude Backend

### Strengths
- High accuracy for complex layouts
- Understands context and semantic relationships
- Native entity extraction with confidence scores
- Handles images, tables, styled content well

### Limitations
- Costs API tokens (included in Claude Max $100/month)
- Slower than pure OCR for simple documents

### Configuration
```python
from extraction_backends import ClaudeExtractionBackend

backend = ClaudeExtractionBackend(
    api_key="sk-...",  # or ANTHROPIC_API_KEY env var
    model="claude-sonnet-4-20250514"
)
```

### Entity Types (Default)
- medication
- person
- date
- condition
- vital_sign
- procedure
- instruction
- allergy

### Usage
```python
result = await backend.extract(
    file_path="/path/to/document.pdf",
    extract_entities=True,
    entity_types=["medication", "person", "date"]
)
```

## Docling Backend

### Strengths
- Free (self-hosted)
- Good for batch processing
- Fast for simple documents
- No token costs

### Limitations
- May miss styled/formatted content (CRITICAL)
- Less accurate for complex layouts
- No built-in entity extraction (needs LLM pass)

### Configuration
```python
from extraction_backends import DoclingExtractionBackend

backend = DoclingExtractionBackend(
    api_url="https://docling.leadingai.info",  # or DOCLING_API_URL env var
    timeout=180
)
```

### API Endpoint
```
POST /v1/convert/file
Content-Type: multipart/form-data
Field: files (not "file")
```

### Usage
```python
result = await backend.extract(
    file_path="/path/to/document.pdf",
    extract_entities=False  # Not supported natively
)
```

## Validation Layer

Both backends support validation to catch:
- **Hallucinations**: Text not in original document
- **Missing content**: Critical sections omitted
- **Confidence downgrade**: Uncertain extractions marked LOW

### Claude Validation
```python
# Checks entity names appear in source text
for entity in result.entities:
    if entity.name not in result.raw_text:
        result.validation_warnings.append(
            f"Entity '{entity.name}' may be inferred"
        )
        entity.confidence = ExtractionConfidence.LOW
```

### Docling Validation
```python
# Checks for minimal content (may indicate failed extraction)
if len(result.raw_text) < 50:
    result.validation_errors.append(
        "Extraction returned minimal content"
    )
```

## Adding New Backends

To add a new extraction backend:

1. Create new file in `extraction_backends/`
2. Inherit from `ExtractionBackend`
3. Implement required methods:

```python
from .base import ExtractionBackend, ExtractionResult

class NewBackend(ExtractionBackend):
    @property
    def name(self) -> str:
        return "new_backend"

    @property
    def supports_batch(self) -> bool:
        return True

    async def extract(
        self,
        file_path: str,
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> ExtractionResult:
        # Implementation
        pass

    async def extract_batch(
        self,
        file_paths: List[str],
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> List[ExtractionResult]:
        # Implementation
        pass

    async def validate_extraction(
        self,
        result: ExtractionResult,
        original_file_path: str
    ) -> ExtractionResult:
        # Implementation
        pass
```

4. Add to `__init__.py`:
```python
from .new_backend import NewBackend
```

5. Add to `ExtractionBackendType` enum in `document_processor.py`:
```python
class ExtractionBackendType(Enum):
    CLAUDE = "claude"
    DOCLING = "docling"
    NEW_BACKEND = "new_backend"  # Add this
```

## Testing Backends

### Health Check
```python
# Docling
is_healthy = await docling_backend.health_check()

# Claude (always available if API key valid)
```

### Supported Formats
```python
# Check if format supported
is_supported = backend.is_format_supported("/path/to/file.pdf")

# Get all supported formats
formats = backend.get_supported_formats()
# Claude: ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp']
# Docling: ['.pdf', '.docx', '.doc', '.pptx', '.html', '.md', '.txt']
```

## Related Documentation

- [Document Processor](./DOCUMENT_PROCESSOR.md) - How backends are used
- [Knowledge Ingestion](./KNOWLEDGE_INGESTION.md) - Full pipeline
- [Docling Service](../infrastructure/DOCLING_SERVICE.md) - Self-hosted setup

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
