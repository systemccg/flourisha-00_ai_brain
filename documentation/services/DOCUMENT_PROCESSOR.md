# Document Processor Service

The DocumentProcessor handles extraction of text and entities from various document formats using pluggable backends.

## Location

`/root/flourisha/00_AI_Brain/services/document_processor.py`

## Overview

```python
from services.document_processor import (
    DocumentProcessor,
    ExtractionBackendType,
    get_document_processor,
    process_file
)
```

## Extraction Backends

The processor uses a **Strategy pattern** with swappable backends:

| Backend | Enum Value | Best For | Cost |
|---------|------------|----------|------|
| **Claude** | `CLAUDE` | Accuracy, complex layouts, entity extraction | API tokens (included in Max) |
| **Docling** | `DOCLING` | Batch processing, simple documents | Free (self-hosted) |
| **Legacy** | `LEGACY` | Backward compatibility | Free (local) |

### Backend Selection Logic

```
1. Try primary backend (default: Claude)
2. Validate extraction if enabled
3. If validation fails → try fallback backend
4. If fallback fails → raise error
```

## Usage Examples

### Simple Processing
```python
from services.document_processor import process_file

# Uses Claude by default with Docling fallback
text, metadata = await process_file(
    file_path="/path/to/document.pdf",
    use_new_backend=True,
    extract_entities=True
)
```

### Specify Backend
```python
from services.document_processor import get_document_processor, ExtractionBackendType

# Use Docling explicitly (for batch processing)
processor = await get_document_processor(
    default_backend=ExtractionBackendType.DOCLING,
    fallback_backend=None  # No fallback
)

result = await processor.extract_with_backend(file_path)
```

### Legacy Mode
```python
# Use original pdfplumber-based extraction
text, metadata = await process_file(
    file_path="/path/to/document.pdf",
    use_new_backend=False  # Uses pdfplumber
)
```

## Supported Formats

| Type | Extensions |
|------|------------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| Text | `.txt`, `.md`, `.markdown` |
| Spreadsheet | `.xlsx`, `.xls`, `.csv` |
| Image | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` |

## Configuration

### Default Settings
- **Max file size**: 100MB
- **Default backend**: Claude
- **Fallback backend**: Docling
- **Validation**: Enabled

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-...  # Required for Claude backend
DOCLING_API_URL=https://docling.leadingai.info  # Docling endpoint
```

## API Reference

### DocumentProcessor Class

```python
class DocumentProcessor:
    def __init__(
        self,
        default_backend: ExtractionBackendType = ExtractionBackendType.CLAUDE,
        fallback_backend: Optional[ExtractionBackendType] = ExtractionBackendType.DOCLING,
        validate_extractions: bool = True
    )
```

### Key Methods

#### extract_with_backend()
```python
async def extract_with_backend(
    self,
    file_path: str,
    backend_type: Optional[ExtractionBackendType] = None,
    extract_entities: bool = True,
    entity_types: Optional[List[str]] = None
) -> ExtractionResult
```

Returns `ExtractionResult` with:
- `raw_text`: Extracted text
- `markdown`: Formatted markdown (if available)
- `entities`: List of `ExtractedEntity`
- `relationships`: List of `ExtractedRelationship`
- `confidence`: `ExtractionConfidence` level
- `validation_warnings`: List of warnings
- `validation_errors`: List of errors

#### process_document()
```python
async def process_document(
    self,
    file_path: str,
    use_new_backend: bool = True,
    extract_entities: bool = True,
    entity_types: Optional[List[str]] = None
) -> Tuple[str, Dict]
```

Returns legacy format `(text, metadata)` for backward compatibility.

## Validation

The processor validates extractions to catch:
- Hallucinated content (text not in original)
- Missing critical sections
- Malformed entities

### Validation Levels

| Confidence | Meaning |
|------------|---------|
| `HIGH` | Structured data, clear text |
| `MEDIUM` | Some ambiguity, OCR required |
| `LOW` | Poor quality, uncertain |

## Critical Warning

**Docling may miss styled content boxes** (e.g., medication instructions in colored boxes). This was discovered when Docling missed a "STOP CHLORELLA" instruction in a medical document.

**For medical or critical documents, always use Claude backend.**

## Error Handling

```python
try:
    result = await processor.extract_with_backend(file_path)
except FileNotFoundError:
    # File doesn't exist
except ValueError:
    # Unsupported format or validation error
except RuntimeError:
    # All backends failed
```

## Related Documentation

- [Extraction Backends](./EXTRACTION_BACKENDS.md) - Backend details
- [Knowledge Ingestion](./KNOWLEDGE_INGESTION.md) - Full pipeline
- [Docling Service](../infrastructure/DOCLING_SERVICE.md) - Self-hosted OCR

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
