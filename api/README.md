# Flourisha API

REST API backend for the Flourisha AI Brain system.

## Quick Start

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --port 8000 --reload
```

## Endpoints

- `GET /api/health` - Health check
- `GET /docs` - OpenAPI documentation

## Development

Built with FastAPI and managed with uv.
