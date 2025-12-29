"""
Flourisha API - Main Application

FastAPI backend for the Flourisha AI Brain system.
Provides REST endpoints for content processing, knowledge management,
and productivity tools.

Run with: uv run uvicorn main:app --port 8000 --reload
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.response import APIResponse, HealthStatus, ResponseMeta
from middleware.timing import TimingMiddleware
from middleware.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from middleware.auth import get_current_user, get_optional_user, UserContext
from middleware.rate_limit import RateLimitMiddleware, get_rate_limit_status
from config import get_settings, validate_startup_config, Settings


# Load settings from environment
settings = get_settings()

# OpenAPI Tags with descriptions for documentation grouping
OPENAPI_TAGS = [
    {
        "name": "System",
        "description": "System health, status, and root endpoints. No authentication required for health checks.",
    },
    {
        "name": "Auth",
        "description": "Authentication and user profile endpoints. Requires Firebase JWT Bearer token.",
    },
    {
        "name": "Search",
        "description": "Unified semantic search across vector store, knowledge graph, and documents.",
    },
    {
        "name": "YouTube",
        "description": "YouTube channel management, playlist processing, and video transcription.",
    },
    {
        "name": "Documents",
        "description": "Document upload, processing, and extraction. Supports PDF, images, and text files.",
    },
    {
        "name": "Ingestion",
        "description": "Knowledge ingestion pipeline for processing content into vector/graph stores.",
    },
    {
        "name": "Graph",
        "description": "Neo4j knowledge graph queries, entity relationships, and graph traversal.",
    },
    {
        "name": "Reports",
        "description": "Morning reports, productivity analysis, and daily briefings.",
    },
    {
        "name": "OKRs",
        "description": "Objectives and Key Results tracking, progress updates, and rollups.",
    },
    {
        "name": "Energy",
        "description": "Energy tracking (1-10), focus quality monitoring, and productivity patterns.",
    },
    {
        "name": "Skills",
        "description": "PAI Skills registry, execution, and configuration management.",
    },
    {
        "name": "PARA",
        "description": "Projects, Areas, Resources, Archives file system navigation and management.",
    },
    {
        "name": "Queue",
        "description": "Background processing queue management and job status.",
    },
    {
        "name": "Feedback",
        "description": "Extraction feedback for improving document processing accuracy.",
    },
    {
        "name": "Context Card",
        "description": "Context cards for quick access to relevant information.",
    },
    {
        "name": "Gmail",
        "description": "Gmail integration for email processing and knowledge extraction.",
    },
    {
        "name": "Voice",
        "description": "Voice synthesis using ElevenLabs TTS with agent-specific voices.",
    },
    {
        "name": "Roadmap",
        "description": "Daily roadmap generation synthesizing OKRs, energy, and priorities.",
    },
    {
        "name": "Health Dashboard",
        "description": "System health monitoring for Supabase, Neo4j, and services.",
    },
    {
        "name": "Sync",
        "description": "Flourisha sync with Google Drive using rclone bisync.",
    },
    {
        "name": "Transcript",
        "description": "YouTube transcript retrieval with caching and multiple methods.",
    },
    {
        "name": "A2A",
        "description": "Agent-to-Agent protocol registry for agent discovery and communication.",
    },
    {
        "name": "Workspace",
        "description": "Multi-tenant workspace management, settings, and configuration.",
    },
    {
        "name": "Invitations",
        "description": "Workspace invitation management for team collaboration.",
    },
    {
        "name": "Groups",
        "description": "User group management for permissions and sharing.",
    },
    {
        "name": "Profile",
        "description": "User profile management, preferences, and settings.",
    },
    {
        "name": "Integrations",
        "description": "Third-party integration management (Slack, Notion, etc.).",
    },
    {
        "name": "Billing",
        "description": "Subscription management, usage tracking, and payment processing.",
    },
    {
        "name": "Agents",
        "description": "AI agent registry, execution, and monitoring.",
    },
    {
        "name": "Fabric",
        "description": "Fabric pattern execution for content transformation.",
    },
    {
        "name": "Crons",
        "description": "Scheduled task endpoints triggered by pg_cron or systemd timers.",
    },
    {
        "name": "Migrations",
        "description": "Database migration management and schema introspection (admin only).",
    },
    {
        "name": "Webhooks",
        "description": "Incoming webhooks from ClickUp, Gmail, Stripe, and energy tracking.",
    },
    {
        "name": "ClickUp",
        "description": "ClickUp task management integration and synchronization.",
    },
    {
        "name": "Chrome Extension",
        "description": "APIs for Chrome browser extension: quick capture, page saving, sync, and energy tracking.",
    },
    {
        "name": "Mobile App",
        "description": "APIs for React Native mobile app: device registration, offline sync, voice notes, and mobile-optimized endpoints.",
    },
    {
        "name": "Skills Database",
        "description": "Database-backed skills storage with filesystem sync. Supports CRUD operations and migration from ~/.claude/skills/.",
    },
]

# Create FastAPI app with enhanced OpenAPI configuration
app = FastAPI(
    title="Flourisha API",
    description="""
## Flourisha AI Brain REST API

**Knowledge management, content processing, and productivity tools for personal AI infrastructure.**

### Architecture

The API follows a **Five Pillars** architecture:

| Pillar | Purpose | Key Endpoints |
|--------|---------|---------------|
| **INGEST** | Content ingestion | `/youtube`, `/documents`, `/gmail` |
| **KNOW** | Knowledge storage | `/search`, `/graph`, `/ingestion` |
| **THINK** | Strategic command | `/reports`, `/okrs`, `/roadmap` |
| **EXECUTE** | Agentic operations | `/skills`, `/agents`, `/fabric` |
| **GROW** | System evolution | `/feedback`, `/health-dashboard` |

### Authentication

Most endpoints require a **Firebase JWT Bearer token** in the Authorization header:

```
Authorization: Bearer <firebase-jwt-token>
```

**Public endpoints** (no auth required):
- `GET /api/health` - Health check
- `GET /api/crons/health` - Cron health
- `GET /api/migrations/health` - Migration health
- `POST /api/webhooks/*` - Webhook receivers (use signature verification)

**Admin endpoints** require additional `X-Admin-Secret` or `X-Cron-Secret` header:
- `POST /api/crons/trigger/*` - Trigger cron jobs
- `POST /api/migrations/apply` - Apply migrations
- `POST /api/migrations/execute` - Execute SQL

### Response Format

All responses follow a consistent format:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "uuid",
    "duration_ms": 123,
    "timestamp": "2025-12-29T12:00:00-08:00"
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Request body validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |
| 503 | Service Unavailable - Dependency unavailable |

### Rate Limiting

Rate limits are applied per user/API key:
- **Standard**: 1000 requests/hour
- **Search**: 100 requests/minute (expensive operations)
- **Webhooks**: Unlimited (signature verified)

### Multi-Tenant Architecture

All data is isolated by `tenant_id`. Row-Level Security (RLS) is enforced at the database level.
Users can only access data within their tenant unless explicitly shared via groups.

### Timezone

All timestamps use **Pacific Time (America/Los_Angeles)** unless otherwise specified.
""",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": "Flourisha Support",
        "url": "https://github.com/systemccg/flourisha-00_ai_brain",
        "email": "gwasmuth@gmail.com",
    },
    license_info={
        "name": "Private - All Rights Reserved",
        "url": "https://github.com/systemccg/flourisha-00_ai_brain/blob/main/LICENSE",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local Development"},
        {"url": "https://api.flourisha.app", "description": "Production (future)"},
    ],
)

# Exception handlers - consistent APIResponse format for all errors
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Request timing middleware - adds request_id and timing
app.add_middleware(TimingMiddleware)

# Rate limiting middleware - per-user/IP limits
app.add_middleware(RateLimitMiddleware)

# CORS Configuration - from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    validate_startup_config()


@app.get("/api/health", response_model=APIResponse[HealthStatus], tags=["System"])
async def health_check(request: Request) -> APIResponse[HealthStatus]:
    """
    Health check endpoint.

    Returns current server status, API version, and timestamp.
    Used by monitoring systems and frontend health checks.
    """
    # Use Pacific time as per PAI conventions
    pacific = ZoneInfo("America/Los_Angeles")
    now = datetime.now(pacific)

    # Get timing metadata from middleware
    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=HealthStatus(
            status="healthy",
            version=settings.api_version,
            timestamp=now.isoformat(),
        ),
        meta=ResponseMeta(**meta_dict),
    )


@app.get("/", tags=["System"])
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Flourisha API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/rate-limit", tags=["System"])
async def rate_limit_status(request: Request) -> APIResponse[dict]:
    """
    Get current rate limit status for the caller.

    Returns rate limit configuration and current usage.
    No authentication required - works for anonymous and authenticated users.

    Response includes:
    - identifier: Truncated identifier (user ID or IP hash)
    - is_authenticated: Whether caller is authenticated
    - limit: Maximum requests in window
    - window_seconds: Rate limit window duration
    - path: Current request path
    """
    status = get_rate_limit_status(request)
    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=status,
        meta=ResponseMeta(**meta_dict),
    )


@app.get("/api/me", tags=["Auth"])
async def get_me(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Get current authenticated user info.

    Requires: Valid Firebase JWT in Authorization header

    Returns user profile extracted from JWT claims.
    """
    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data={
            "uid": user.uid,
            "email": user.email,
            "name": user.name,
            "email_verified": user.email_verified,
            "tenant_id": user.tenant_id,
            "roles": user.roles,
        },
        meta=ResponseMeta(**meta_dict),
    )


# Router imports
from routers.search import router as search_router
from routers.clickup import router as clickup_router
from routers.youtube import router as youtube_router
from routers.webhooks import router as webhooks_router
from routers.documents import router as documents_router
from routers.ingestion import router as ingestion_router
from routers.reports import router as reports_router
from routers.graph import router as graph_router
from routers.okrs import router as okrs_router
from routers.energy import router as energy_router
from routers.skills import router as skills_router
from routers.para import router as para_router
from routers.queue import router as queue_router
from routers.feedback import router as feedback_router
from routers.context_card import router as context_card_router
from routers.gmail import router as gmail_router
from routers.voice import router as voice_router
from routers.roadmap import router as roadmap_router
from routers.health_dashboard import router as health_dashboard_router
from routers.sync import router as sync_router
from routers.transcript import router as transcript_router
from routers.a2a import router as a2a_router
from routers.workspace import router as workspace_router
from routers.invitations import router as invitations_router
from routers.groups import router as groups_router
from routers.profile import router as profile_router
from routers.integrations import router as integrations_router
from routers.billing import router as billing_router
from routers.agents import router as agents_router
from routers.fabric import router as fabric_router
from routers.crons import router as crons_router
from routers.migrations import router as migrations_router
from routers.chrome_extension import router as chrome_extension_router
from routers.mobile_app import router as mobile_app_router
from routers.skills_db import router as skills_db_router

# Include routers
app.include_router(search_router)
app.include_router(clickup_router)
app.include_router(youtube_router)
app.include_router(webhooks_router)
app.include_router(documents_router)
app.include_router(ingestion_router)
app.include_router(reports_router)
app.include_router(graph_router)
app.include_router(okrs_router)
app.include_router(energy_router)
app.include_router(skills_router)
app.include_router(para_router)
app.include_router(queue_router)
app.include_router(feedback_router)
app.include_router(context_card_router)
app.include_router(gmail_router)
app.include_router(voice_router)
app.include_router(roadmap_router)
app.include_router(health_dashboard_router)
app.include_router(sync_router)
app.include_router(transcript_router)
app.include_router(a2a_router)
app.include_router(workspace_router)
app.include_router(invitations_router)
app.include_router(groups_router)
app.include_router(profile_router)
app.include_router(integrations_router)
app.include_router(billing_router)
app.include_router(agents_router)
app.include_router(fabric_router)
app.include_router(crons_router)
app.include_router(migrations_router)
app.include_router(chrome_extension_router)
app.include_router(mobile_app_router)
app.include_router(skills_db_router)


# Custom OpenAPI schema with security definitions
def custom_openapi():
    """Generate custom OpenAPI schema with security schemes and examples."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
        contact=app.contact,
        license_info=app.license_info,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Firebase JWT token. Get from Firebase Authentication.",
        },
        "AdminSecret": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Admin-Secret",
            "description": "Admin secret for privileged operations (migrations, SQL execution).",
        },
        "CronSecret": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Cron-Secret",
            "description": "Internal secret for scheduled task endpoints.",
        },
        "WebhookSignature": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Signature",
            "description": "HMAC-SHA256 signature for webhook verification.",
        },
    }

    # Add global security (Bearer auth by default)
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Add example responses to schema
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    # Add common response examples
    openapi_schema["components"]["examples"] = {
        "SuccessResponse": {
            "summary": "Successful response",
            "value": {
                "success": True,
                "data": {"example": "data"},
                "error": None,
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "duration_ms": 45,
                    "timestamp": "2025-12-29T12:00:00-08:00",
                },
            },
        },
        "ErrorResponse": {
            "summary": "Error response",
            "value": {
                "success": False,
                "data": None,
                "error": "Resource not found",
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440001",
                    "duration_ms": 12,
                    "timestamp": "2025-12-29T12:00:00-08:00",
                },
            },
        },
        "UnauthorizedResponse": {
            "summary": "Unauthorized response",
            "value": {
                "success": False,
                "data": None,
                "error": "Invalid or expired token",
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440002",
                    "duration_ms": 5,
                    "timestamp": "2025-12-29T12:00:00-08:00",
                },
            },
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
