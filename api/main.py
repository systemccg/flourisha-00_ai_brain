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
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.response import APIResponse, HealthStatus, ResponseMeta
from middleware.timing import TimingMiddleware
from middleware.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from middleware.auth import get_current_user, get_optional_user, UserContext
from config import get_settings, validate_startup_config, Settings


# Load settings from environment
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Flourisha API",
    description="REST API for Flourisha AI Brain - Knowledge management, content processing, and productivity tools",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Exception handlers - consistent APIResponse format for all errors
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Request timing middleware - adds request_id and timing
app.add_middleware(TimingMiddleware)

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
