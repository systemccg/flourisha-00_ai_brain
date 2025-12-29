"""
Integrations Hub Router

Centralized management for all external integrations (email, calendar, storage, ERP, CRM).
Supports OAuth, API key, MCP, and Skill-based integrations.

Based on FRONTEND_FEATURE_REGISTRY section 0.7: Integrations Hub
"""
import os
import sys
import uuid
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException, status
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.integrations import (
    IntegrationType,
    IntegrationCategory,
    ConnectionStatus,
    SyncFrequency,
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationConnection,
    IntegrationWithConnection,
    IntegrationListResponse,
    IntegrationDetailResponse,
    OAuthInitiateResponse,
    OAuthCallbackRequest,
    DisconnectResponse,
    HealthCheckResponse,
    SyncTriggerRequest,
    SyncTriggerResponse,
    SyncLogEntry,
    SyncLogsResponse,
    UpdateSettingsRequest,
)
from middleware.auth import get_current_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/integrations", tags=["Integrations Hub"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Integration Catalog (Static definitions) ===

INTEGRATION_CATALOG: Dict[str, IntegrationDefinition] = {
    "gmail": IntegrationDefinition(
        id="gmail",
        name="Gmail",
        description="Email integration for reading and syncing Gmail messages",
        category=IntegrationCategory.EMAIL,
        type=IntegrationType.OAUTH,
        icon_url="/icons/gmail.svg",
        docs_url="https://developers.google.com/gmail/api",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True, webhook=True
        ),
        required_scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify"
        ],
    ),
    "google_calendar": IntegrationDefinition(
        id="google_calendar",
        name="Google Calendar",
        description="Calendar integration for events and scheduling",
        category=IntegrationCategory.CALENDAR,
        type=IntegrationType.OAUTH,
        icon_url="/icons/gcal.svg",
        docs_url="https://developers.google.com/calendar",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True, webhook=True
        ),
        required_scopes=[
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events"
        ],
    ),
    "google_drive": IntegrationDefinition(
        id="google_drive",
        name="Google Drive",
        description="Cloud storage sync via rclone bisync",
        category=IntegrationCategory.STORAGE,
        type=IntegrationType.SKILL,
        icon_url="/icons/gdrive.svg",
        docs_url="https://developers.google.com/drive",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True
        ),
    ),
    "youtube": IntegrationDefinition(
        id="youtube",
        name="YouTube",
        description="Video content processing and playlist management",
        category=IntegrationCategory.CONTENT,
        type=IntegrationType.OAUTH,
        icon_url="/icons/youtube.svg",
        docs_url="https://developers.google.com/youtube",
        capabilities=IntegrationCapability(
            read=True, sync=True
        ),
        required_scopes=[
            "https://www.googleapis.com/auth/youtube.readonly"
        ],
    ),
    "clickup": IntegrationDefinition(
        id="clickup",
        name="ClickUp",
        description="Project management and task tracking",
        category=IntegrationCategory.PROJECT_MANAGEMENT,
        type=IntegrationType.SKILL,
        icon_url="/icons/clickup.svg",
        docs_url="https://clickup.com/api",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True, webhook=True
        ),
    ),
    "neo4j": IntegrationDefinition(
        id="neo4j",
        name="Neo4j",
        description="Knowledge graph database for entity relationships",
        category=IntegrationCategory.DATABASE,
        type=IntegrationType.API_KEY,
        icon_url="/icons/neo4j.svg",
        docs_url="https://neo4j.com/docs/",
        capabilities=IntegrationCapability(
            read=True, write=True, realtime=True
        ),
    ),
    "supabase": IntegrationDefinition(
        id="supabase",
        name="Supabase",
        description="Vector store and relational database",
        category=IntegrationCategory.DATABASE,
        type=IntegrationType.API_KEY,
        icon_url="/icons/supabase.svg",
        docs_url="https://supabase.com/docs",
        capabilities=IntegrationCapability(
            read=True, write=True, realtime=True
        ),
    ),
    "slack": IntegrationDefinition(
        id="slack",
        name="Slack",
        description="Team communication and notifications",
        category=IntegrationCategory.COMMUNICATION,
        type=IntegrationType.MCP,
        icon_url="/icons/slack.svg",
        docs_url="https://api.slack.com/",
        capabilities=IntegrationCapability(
            read=True, write=True, webhook=True, realtime=True
        ),
        is_beta=True,
    ),
    "discord": IntegrationDefinition(
        id="discord",
        name="Discord",
        description="Community communication platform",
        category=IntegrationCategory.COMMUNICATION,
        type=IntegrationType.MCP,
        icon_url="/icons/discord.svg",
        docs_url="https://discord.com/developers/docs",
        capabilities=IntegrationCapability(
            read=True, write=True, realtime=True
        ),
        is_beta=True,
    ),
    "outlook": IntegrationDefinition(
        id="outlook",
        name="Outlook",
        description="Microsoft email and calendar",
        category=IntegrationCategory.EMAIL,
        type=IntegrationType.OAUTH,
        icon_url="/icons/outlook.svg",
        docs_url="https://learn.microsoft.com/en-us/graph/",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True
        ),
        is_beta=True,
    ),
    "onedrive": IntegrationDefinition(
        id="onedrive",
        name="OneDrive",
        description="Microsoft cloud storage",
        category=IntegrationCategory.STORAGE,
        type=IntegrationType.MCP,
        icon_url="/icons/onedrive.svg",
        docs_url="https://learn.microsoft.com/en-us/graph/",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True
        ),
        is_beta=True,
    ),
    "salesforce": IntegrationDefinition(
        id="salesforce",
        name="Salesforce",
        description="CRM and sales automation",
        category=IntegrationCategory.CRM,
        type=IntegrationType.MCP,
        icon_url="/icons/salesforce.svg",
        docs_url="https://developer.salesforce.com/docs",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True
        ),
        is_premium=True,
        is_beta=True,
    ),
    "hubspot": IntegrationDefinition(
        id="hubspot",
        name="HubSpot",
        description="Marketing and CRM platform",
        category=IntegrationCategory.CRM,
        type=IntegrationType.MCP,
        icon_url="/icons/hubspot.svg",
        docs_url="https://developers.hubspot.com/docs",
        capabilities=IntegrationCapability(
            read=True, write=True, sync=True
        ),
        is_premium=True,
        is_beta=True,
    ),
    "quickbooks": IntegrationDefinition(
        id="quickbooks",
        name="QuickBooks",
        description="Accounting and financial management",
        category=IntegrationCategory.ERP,
        type=IntegrationType.MCP,
        icon_url="/icons/quickbooks.svg",
        docs_url="https://developer.intuit.com/app/developer/qbo/docs",
        capabilities=IntegrationCapability(
            read=True, write=True
        ),
        is_premium=True,
        is_beta=True,
    ),
    "openai": IntegrationDefinition(
        id="openai",
        name="OpenAI",
        description="GPT models for AI processing",
        category=IntegrationCategory.AI,
        type=IntegrationType.API_KEY,
        icon_url="/icons/openai.svg",
        docs_url="https://platform.openai.com/docs",
        capabilities=IntegrationCapability(
            read=True, write=True
        ),
    ),
    "anthropic": IntegrationDefinition(
        id="anthropic",
        name="Anthropic",
        description="Claude models for AI processing",
        category=IntegrationCategory.AI,
        type=IntegrationType.API_KEY,
        icon_url="/icons/anthropic.svg",
        docs_url="https://docs.anthropic.com/",
        capabilities=IntegrationCapability(
            read=True, write=True
        ),
    ),
}


# === In-memory storage for connections (to be replaced with DB) ===
# In production, this would be stored in Supabase

_user_connections: Dict[str, Dict[str, IntegrationConnection]] = {}
_sync_logs: Dict[str, List[SyncLogEntry]] = {}
_oauth_states: Dict[str, Dict[str, Any]] = {}


def _get_user_connections(user_id: str) -> Dict[str, IntegrationConnection]:
    """Get user's integration connections."""
    if user_id not in _user_connections:
        _user_connections[user_id] = {}
    return _user_connections[user_id]


def _get_sync_logs(integration_id: str, user_id: str) -> List[SyncLogEntry]:
    """Get sync logs for an integration."""
    key = f"{user_id}:{integration_id}"
    return _sync_logs.get(key, [])


def _add_sync_log(integration_id: str, user_id: str, log: SyncLogEntry):
    """Add a sync log entry."""
    key = f"{user_id}:{integration_id}"
    if key not in _sync_logs:
        _sync_logs[key] = []
    _sync_logs[key].insert(0, log)
    # Keep only last 100 logs
    _sync_logs[key] = _sync_logs[key][:100]


# === Endpoints ===

@router.get(
    "",
    response_model=APIResponse[IntegrationListResponse],
    summary="List all integrations",
    description="Get all available integrations with user's connection status"
)
async def list_integrations(
    request: Request,
    user: UserContext = Depends(get_current_user),
    category: Optional[IntegrationCategory] = Query(
        None, description="Filter by category"
    ),
    connected_only: bool = Query(
        False, description="Only show connected integrations"
    ),
    include_beta: bool = Query(
        True, description="Include beta integrations"
    ),
) -> APIResponse[IntegrationListResponse]:
    """
    List all available integrations with the current user's connection status.

    Returns the full catalog of integrations, filtered by optional parameters,
    with each integration's connection status for the authenticated user.
    """
    now = datetime.now(PACIFIC)
    meta_dict = request.state.get_meta()

    user_connections = _get_user_connections(user.uid)

    result_integrations: List[IntegrationWithConnection] = []
    connected_count = 0

    for integration_id, integration in INTEGRATION_CATALOG.items():
        # Apply filters
        if category and integration.category != category:
            continue
        if not include_beta and integration.is_beta:
            continue

        # Get connection if exists
        connection = user_connections.get(integration_id)
        is_connected = connection is not None and connection.status == ConnectionStatus.CONNECTED

        if connected_only and not is_connected:
            continue

        if is_connected:
            connected_count += 1

        result_integrations.append(IntegrationWithConnection(
            integration=integration,
            connection=connection,
            is_connected=is_connected,
        ))

    return APIResponse(
        success=True,
        data=IntegrationListResponse(
            integrations=result_integrations,
            total=len(result_integrations),
            connected_count=connected_count,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get(
    "/{integration_id}",
    response_model=APIResponse[IntegrationDetailResponse],
    summary="Get integration details",
    description="Get detailed information about a specific integration"
)
async def get_integration(
    request: Request,
    integration_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[IntegrationDetailResponse]:
    """
    Get detailed information about a specific integration.

    Includes the integration definition, user's connection status,
    and recent sync activity logs.
    """
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    integration = INTEGRATION_CATALOG[integration_id]
    user_connections = _get_user_connections(user.uid)
    connection = user_connections.get(integration_id)

    # Get recent logs (last 10)
    logs = _get_sync_logs(integration_id, user.uid)[:10]

    return APIResponse(
        success=True,
        data=IntegrationDetailResponse(
            integration=integration,
            connection=connection,
            recent_logs=logs,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.post(
    "/{integration_id}/connect",
    response_model=APIResponse[OAuthInitiateResponse],
    summary="Start OAuth flow",
    description="Initiate OAuth authorization for an integration"
)
async def connect_integration(
    request: Request,
    integration_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[OAuthInitiateResponse]:
    """
    Initiate OAuth authorization flow for an integration.

    For OAuth integrations, returns an authorization URL to redirect the user.
    For API key integrations, returns instructions for providing the key.
    For Skill/MCP integrations, returns status of the existing connection.
    """
    now = datetime.now(PACIFIC)
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    integration = INTEGRATION_CATALOG[integration_id]

    # Handle different integration types
    if integration.type == IntegrationType.OAUTH:
        # Generate OAuth state
        state = str(uuid.uuid4())
        expires_at = now + timedelta(minutes=10)

        # Store state for verification
        _oauth_states[state] = {
            "user_id": user.uid,
            "integration_id": integration_id,
            "expires_at": expires_at.isoformat(),
        }

        # Generate auth URL based on provider
        auth_url = _get_oauth_url(integration_id, state, integration.required_scopes)

        return APIResponse(
            success=True,
            data=OAuthInitiateResponse(
                auth_url=auth_url,
                state=state,
                expires_at=expires_at.isoformat(),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    elif integration.type == IntegrationType.API_KEY:
        # For API key integrations, check if already configured
        user_connections = _get_user_connections(user.uid)

        if integration_id in user_connections:
            return APIResponse(
                success=True,
                data=OAuthInitiateResponse(
                    auth_url="",  # No redirect needed
                    state="api_key",
                    expires_at=now.isoformat(),
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Return placeholder - actual API key should be configured via settings
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key integrations must be configured via environment variables or settings. "
                   f"Set the appropriate API key for '{integration_id}'"
        )

    elif integration.type in (IntegrationType.SKILL, IntegrationType.MCP):
        # Skill/MCP integrations are pre-configured at system level
        # Create a connection record if not exists
        user_connections = _get_user_connections(user.uid)

        if integration_id not in user_connections:
            user_connections[integration_id] = IntegrationConnection(
                integration_id=integration_id,
                user_id=user.uid,
                workspace_id="default",  # TODO: Get from user context
                status=ConnectionStatus.CONNECTED,
                connected_at=now,
                settings={},
            )

        return APIResponse(
            success=True,
            data=OAuthInitiateResponse(
                auth_url="",  # No redirect needed
                state="skill_connected",
                expires_at=now.isoformat(),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown integration type: {integration.type}"
    )


@router.post(
    "/{integration_id}/disconnect",
    response_model=APIResponse[DisconnectResponse],
    summary="Disconnect integration",
    description="Revoke access and remove integration connection"
)
async def disconnect_integration(
    request: Request,
    integration_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DisconnectResponse]:
    """
    Disconnect an integration and revoke access.

    Removes the connection record and attempts to revoke tokens
    with the provider if applicable.
    """
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    user_connections = _get_user_connections(user.uid)

    if integration_id not in user_connections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration '{integration_id}' is not connected"
        )

    # Remove connection
    del user_connections[integration_id]

    # TODO: Revoke OAuth tokens with provider

    return APIResponse(
        success=True,
        data=DisconnectResponse(
            success=True,
            integration_id=integration_id,
            message=f"Successfully disconnected from {integration_id}",
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get(
    "/{integration_id}/status",
    response_model=APIResponse[HealthCheckResponse],
    summary="Check connection health",
    description="Verify the integration connection is working"
)
async def check_integration_status(
    request: Request,
    integration_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[HealthCheckResponse]:
    """
    Check the health of an integration connection.

    Verifies tokens are valid, connection is working,
    and reports any issues.
    """
    now = datetime.now(PACIFIC)
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    user_connections = _get_user_connections(user.uid)
    connection = user_connections.get(integration_id)

    if not connection:
        return APIResponse(
            success=True,
            data=HealthCheckResponse(
                integration_id=integration_id,
                status=ConnectionStatus.DISCONNECTED,
                is_healthy=False,
                last_check=now.isoformat(),
                error="Integration not connected",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    # Calculate token expiration
    token_expires_in = None
    if connection.expires_at:
        delta = connection.expires_at - now
        token_expires_in = max(0, int(delta.total_seconds()))

    # Check if token is expired
    is_expired = connection.expires_at and connection.expires_at < now

    if is_expired:
        connection.status = ConnectionStatus.EXPIRED

    # TODO: Actually ping the integration to verify health
    is_healthy = connection.status == ConnectionStatus.CONNECTED and not is_expired

    return APIResponse(
        success=True,
        data=HealthCheckResponse(
            integration_id=integration_id,
            status=connection.status,
            is_healthy=is_healthy,
            last_check=now.isoformat(),
            token_expires_in=token_expires_in,
            error=connection.error_message,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.post(
    "/{integration_id}/sync",
    response_model=APIResponse[SyncTriggerResponse],
    summary="Trigger manual sync",
    description="Start a manual sync for this integration"
)
async def trigger_sync(
    request: Request,
    integration_id: str,
    sync_request: Optional[SyncTriggerRequest] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SyncTriggerResponse]:
    """
    Trigger a manual sync for an integration.

    Queues a sync job and returns tracking information.
    """
    now = datetime.now(PACIFIC)
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    integration = INTEGRATION_CATALOG[integration_id]

    if not integration.capabilities.sync:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration '{integration_id}' does not support sync"
        )

    user_connections = _get_user_connections(user.uid)
    connection = user_connections.get(integration_id)

    if not connection or connection.status != ConnectionStatus.CONNECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration '{integration_id}' is not connected"
        )

    # Generate sync ID
    sync_id = str(uuid.uuid4())

    # Add to sync logs
    log = SyncLogEntry(
        id=sync_id,
        timestamp=now.isoformat(),
        action="sync_started",
        status="running",
        items_processed=0,
        details={
            "full_sync": sync_request.full_sync if sync_request else False,
            "options": sync_request.options if sync_request else {},
        },
    )
    _add_sync_log(integration_id, user.uid, log)

    # Update last sync time
    connection.last_sync = now

    # TODO: Actually queue the sync job
    # For now, simulate immediate completion
    completion_log = SyncLogEntry(
        id=f"{sync_id}_complete",
        timestamp=now.isoformat(),
        action="sync_completed",
        status="success",
        items_processed=0,
        duration_ms=100,
        details={"sync_id": sync_id},
    )
    _add_sync_log(integration_id, user.uid, completion_log)

    return APIResponse(
        success=True,
        data=SyncTriggerResponse(
            integration_id=integration_id,
            sync_id=sync_id,
            status="completed",
            estimated_duration=None,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get(
    "/{integration_id}/logs",
    response_model=APIResponse[SyncLogsResponse],
    summary="Get sync logs",
    description="Get recent sync activity logs for this integration"
)
async def get_sync_logs(
    request: Request,
    integration_id: str,
    user: UserContext = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> APIResponse[SyncLogsResponse]:
    """
    Get sync activity logs for an integration.

    Returns paginated log entries showing sync history,
    errors, and item counts.
    """
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    all_logs = _get_sync_logs(integration_id, user.uid)
    total = len(all_logs)

    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_logs = all_logs[start_idx:end_idx]

    return APIResponse(
        success=True,
        data=SyncLogsResponse(
            logs=page_logs,
            total=total,
            page=page,
            page_size=page_size,
            has_more=end_idx < total,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.patch(
    "/{integration_id}/settings",
    response_model=APIResponse[IntegrationConnection],
    summary="Update integration settings",
    description="Update settings for a connected integration"
)
async def update_integration_settings(
    request: Request,
    integration_id: str,
    settings_update: UpdateSettingsRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[IntegrationConnection]:
    """
    Update settings for a connected integration.

    Allows updating sync frequency and integration-specific settings.
    """
    meta_dict = request.state.get_meta()

    if integration_id not in INTEGRATION_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found"
        )

    user_connections = _get_user_connections(user.uid)
    connection = user_connections.get(integration_id)

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration '{integration_id}' is not connected"
        )

    # Update fields
    if settings_update.sync_frequency is not None:
        connection.sync_frequency = settings_update.sync_frequency

    if settings_update.settings is not None:
        connection.settings.update(settings_update.settings)

    return APIResponse(
        success=True,
        data=connection,
        meta=ResponseMeta(**meta_dict),
    )


# === Helper Functions ===

def _get_oauth_url(integration_id: str, state: str, scopes: List[str]) -> str:
    """
    Generate OAuth authorization URL for a provider.

    In production, this would use proper OAuth libraries and
    retrieve client IDs from secure configuration.
    """
    # Base URLs for common providers
    oauth_urls = {
        "gmail": "https://accounts.google.com/o/oauth2/v2/auth",
        "google_calendar": "https://accounts.google.com/o/oauth2/v2/auth",
        "youtube": "https://accounts.google.com/o/oauth2/v2/auth",
        "outlook": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    }

    base_url = oauth_urls.get(integration_id)
    if not base_url:
        return f"/api/integrations/{integration_id}/oauth-not-configured"

    # Get client ID from environment
    client_id = os.environ.get(f"{integration_id.upper()}_CLIENT_ID", "")
    redirect_uri = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/api/integrations/callback")

    # Build URL (simplified - real implementation would use proper OAuth library)
    scope_str = " ".join(scopes)

    if "google" in base_url:
        return (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope_str}&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
    elif "microsoft" in base_url:
        return (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope_str}&"
            f"state={state}"
        )

    return base_url


@router.get(
    "/callback",
    summary="OAuth callback",
    description="Handle OAuth callback from providers",
    include_in_schema=False,  # Hide from OpenAPI docs
)
async def oauth_callback(
    request: Request,
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State token"),
):
    """
    Handle OAuth callback from providers.

    Exchanges the authorization code for tokens and creates
    the integration connection.
    """
    now = datetime.now(PACIFIC)

    # Verify state
    if state not in _oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )

    state_data = _oauth_states.pop(state)

    # Check expiration
    expires_at = datetime.fromisoformat(state_data["expires_at"])
    if now > expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State token expired"
        )

    user_id = state_data["user_id"]
    integration_id = state_data["integration_id"]

    # TODO: Exchange code for tokens with provider
    # For now, simulate success

    # Create connection
    user_connections = _get_user_connections(user_id)
    user_connections[integration_id] = IntegrationConnection(
        integration_id=integration_id,
        user_id=user_id,
        workspace_id="default",  # TODO: Get from context
        status=ConnectionStatus.CONNECTED,
        connected_at=now,
        expires_at=now + timedelta(hours=1),  # Simulated expiration
        settings={},
    )

    # Redirect to frontend success page
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    return {
        "success": True,
        "message": f"Successfully connected to {integration_id}",
        "redirect_url": f"{frontend_url}/settings/integrations?connected={integration_id}",
    }


@router.get(
    "/categories",
    response_model=APIResponse[List[str]],
    summary="List integration categories",
    description="Get all available integration categories"
)
async def list_categories(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[str]]:
    """Get all available integration categories."""
    meta_dict = request.state.get_meta()

    categories = [cat.value for cat in IntegrationCategory]

    return APIResponse(
        success=True,
        data=categories,
        meta=ResponseMeta(**meta_dict),
    )
