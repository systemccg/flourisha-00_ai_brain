# Docling Service

Self-hosted document OCR and conversion service.

## Overview

Docling is a free, self-hosted document extraction service. It provides good text extraction for simple documents but has limitations with styled content.

## Service Details

| Setting | Value |
|---------|-------|
| **URL** | https://docling.leadingai.info |
| **Port** | 5001 (internal) |
| **Container** | `quay.io/docling-project/docling-serve:latest` |
| **Proxy** | Traefik reverse proxy |

## Critical Warning

**Docling may miss styled content boxes.**

During testing with a medical document, Docling failed to extract a "STOP CHLORELLA" instruction that appeared in a colored/styled box. Claude's PDF reading extracted it correctly.

**For medical or critical documents, use the Claude backend instead.**

## API Endpoints

### Health Check
```bash
curl https://docling.leadingai.info/health
```

### Convert File
```bash
curl -X POST https://docling.leadingai.info/v1/convert/file \
  -F "files=@document.pdf"
```

**Important**: The field name is `files` (plural), not `file`.

### Response Format
```json
{
  "document": {
    "filename": "document.pdf",
    "md_content": "# Document Title\n\nExtracted markdown content...",
    "metadata": {
      "pages": 5,
      "created": "2024-01-15"
    }
  }
}
```

## Docker Configuration

### docker-compose.yml
Location: `/root/docling/docker-compose.yml`

```yaml
services:
  docling:
    image: quay.io/docling-project/docling-serve:latest
    container_name: docling
    restart: unless-stopped
    networks:
      - traefik
    volumes:
      - docling_models:/root/.cache/docling
      - docling_hf:/root/.cache/huggingface
      - ./documents:/app/documents
    environment:
      - OMP_NUM_THREADS=4
      - MKL_NUM_THREADS=4
      - OPENBLAS_NUM_THREADS=4
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.docling.rule=Host(`docling.leadingai.info`)"
      - "traefik.http.routers.docling.entrypoints=websecure"
      - "traefik.http.routers.docling.tls=true"
      - "traefik.http.routers.docling.tls.certresolver=letsencrypt"
      - "traefik.http.services.docling.loadbalancer.server.port=5001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s

networks:
  traefik:
    external: true

volumes:
  docling_models:
  docling_hf:
```

### Traefik Configuration
Location: `/root/traefik/dynamic-conf.yml`

```yaml
http:
  routers:
    docling:
      rule: "Host(`docling.leadingai.info`)"
      service: docling-service
      tls:
        certResolver: letsencrypt
      entryPoints:
        - websecure

  services:
    docling-service:
      loadBalancer:
        servers:
          - url: "http://docling:5001"
```

## Python Integration

### DoclingExtractionBackend
Location: `/root/flourisha/00_AI_Brain/services/extraction_backends/docling_backend.py`

```python
from services.extraction_backends import DoclingExtractionBackend

backend = DoclingExtractionBackend(
    api_url="https://docling.leadingai.info",
    timeout=180
)

result = await backend.extract(
    file_path="/path/to/document.pdf",
    extract_entities=False  # Not natively supported
)

print(result.raw_text)
print(result.markdown)
```

### Via Document Processor

```python
from services.document_processor import get_document_processor, ExtractionBackendType

processor = await get_document_processor(
    default_backend=ExtractionBackendType.DOCLING
)

text, metadata = await processor.process_document(
    file_path="/path/to/document.pdf"
)
```

## Supported Formats

| Format | Extensions |
|--------|------------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| PowerPoint | `.pptx` |
| HTML | `.html` |
| Markdown | `.md` |
| Text | `.txt` |

## Operations

### Start Service
```bash
cd /root/docling
docker compose up -d
```

### Check Status
```bash
docker ps | grep docling
curl https://docling.leadingai.info/health
```

### View Logs
```bash
docker logs docling -f
```

### Restart Service
```bash
docker compose restart
```

### Update Image
```bash
docker compose pull
docker compose up -d
```

## Resource Usage

| Resource | Limit | Typical |
|----------|-------|---------|
| Memory | 8GB | 2-4GB idle, 6GB processing |
| CPU | No limit | Varies with document size |
| Disk | ~2GB | Model cache |

## Troubleshooting

### Service Not Starting
```bash
# Check logs
docker logs docling

# Check memory
docker stats docling

# Restart with fresh state
docker compose down
docker compose up -d
```

### Slow Processing
- Large PDFs take time (2-3 min for 50+ pages)
- Model loading on first request (~60s)
- Check memory isn't swapping

### Missing Content
If content is missing from extraction:
1. Check if content is in styled boxes (known limitation)
2. Try Claude backend for critical documents
3. Verify document isn't corrupted

### Connection Refused
1. Check service is running: `docker ps`
2. Check Traefik routing: `docker logs traefik`
3. Verify DNS: `dig docling.leadingai.info`

## Comparison: Claude vs Docling

| Feature | Claude | Docling |
|---------|--------|---------|
| **Accuracy** | Excellent | Good |
| **Styled content** | Yes | May miss |
| **Entity extraction** | Built-in | Requires LLM |
| **Cost** | API tokens | Free |
| **Speed** | Moderate | Fast |
| **Best for** | Critical docs | Batch processing |

## Related Documentation

- [Extraction Backends](../services/EXTRACTION_BACKENDS.md) - All backend options
- [Document Processor](../services/DOCUMENT_PROCESSOR.md) - How backends are used
- [Knowledge Ingestion](../services/KNOWLEDGE_INGESTION.md) - Full pipeline

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
