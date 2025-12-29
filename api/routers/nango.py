"""
Nango Integration Manager Router

API endpoints for Nango unified OAuth management.
Nango provides connection management for 500+ APIs with automatic token refresh.

Nango API Reference: https://docs.nango.dev/reference/api

Task: [4.3] Nango Integration Manager
Pillar: PLATFORM - Secure, scalable integration infrastructure
"""
import os
import sys
import uuid
import json
import logging
import httpx
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import (
    APIRouter, Depends, Request, Query, HTTPException, status,
    BackgroundTasks
)
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.nango import (
    NangoAuthType,
    NangoConnectionStatus,
    NangoSyncStatus,
    NangoSyncType,
    NangoIntegrationProvider,
    NangoIntegrationConfig,
    NangoIntegrationListResponse,
    NangoConnection,
    NangoConnectionListResponse,
    NangoConnectionCredentials,
    CreateConnectionRequest,
    OAuthConnectResponse,
    ConnectionTokenResponse,
    NangoSyncRun,
    NangoSyncRunListResponse,
    TriggerSyncRequest,
    TriggerSyncResponse,
    SyncRecordsRequest,
    SyncRecordsResponse,
    ActionTriggerRequest,
    ActionTriggerResponse,
    NangoWebhookEvent,
    NangoWebhookType,
    NangoEnvironment,
    NangoConfigStatus,
    UpdateNangoConfigRequest,
    NangoProviderInfo,
    NangoProviderListResponse,
    NangoLogEntry,
    NangoLogListResponse,
)
from middleware.auth import get_current_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nango", tags=["Nango OAuth Manager"])

# Pacific timezone
PACIFIC = ZoneInfo("America/Los_Angeles")

# Nango API configuration
NANGO_API_BASE = os.environ.get("NANGO_API_URL", "https://api.nango.dev")


def get_response_meta() -> ResponseMeta:
    """Generate response metadata."""
    return ResponseMeta(
        request_id=f"req_{uuid.uuid4().hex[:12]}",
        duration_ms=0,
        timestamp=datetime.now(PACIFIC).isoformat()
    )


def get_nango_headers() -> Dict[str, str]:
    """Get Nango API headers with authentication."""
    secret_key = os.environ.get("NANGO_SECRET_KEY", "")
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nango secret key not configured. Set NANGO_SECRET_KEY environment variable."
        )
    return {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }


def get_nango_public_key() -> str:
    """Get Nango public key for frontend OAuth flows."""
    return os.environ.get("NANGO_PUBLIC_KEY", "")


# === Configuration Endpoints ===

@router.get("/config/status")
async def get_config_status(
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Get Nango API configuration status.

    Returns whether API is configured, current environment info,
    and counts of integrations and connections.
    """
    secret_key = os.environ.get("NANGO_SECRET_KEY", "")
    public_key = os.environ.get("NANGO_PUBLIC_KEY", "")
    callback_url = os.environ.get("NANGO_CALLBACK_URL", "")

    is_configured = bool(secret_key)
    is_valid = False
    environment = None
    integrations_count = 0
    connections_count = 0

    if is_configured:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Verify key by listing integrations
                response = await client.get(
                    f"{NANGO_API_BASE}/config",
                    headers=get_nango_headers()
                )
                if response.status_code == 200:
                    is_valid = True
                    data = response.json()
                    environment = data.get("environment", {}).get("name")

                # Get counts
                if is_valid:
                    int_resp = await client.get(
                        f"{NANGO_API_BASE}/integrations",
                        headers=get_nango_headers()
                    )
                    if int_resp.status_code == 200:
                        integrations_count = len(int_resp.json().get("integrations", []))

                    conn_resp = await client.get(
                        f"{NANGO_API_BASE}/connections",
                        headers=get_nango_headers()
                    )
                    if conn_resp.status_code == 200:
                        connections_count = len(conn_resp.json().get("connections", []))
        except httpx.RequestError as e:
            logger.warning(f"Failed to verify Nango configuration: {e}")

    config_status = NangoConfigStatus(
        is_configured=is_configured,
        is_valid=is_valid,
        environment=environment,
        base_url=NANGO_API_BASE,
        callback_url=callback_url or None,
        integrations_count=integrations_count,
        connections_count=connections_count,
        version="0.44.0"  # SDK version we're compatible with
    )

    return APIResponse(
        success=True,
        data=config_status.model_dump(),
        meta=get_response_meta()
    )


@router.patch("/config")
async def update_config(
    config_update: UpdateNangoConfigRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Update Nango configuration settings.

    Updates webhook URL, callback URL, and default connection config.
    Note: Environment variables must be updated separately for secret keys.
    """
    try:
        updates = {}
        if config_update.webhook_url:
            updates["webhook_url"] = config_update.webhook_url
        if config_update.callback_url:
            updates["callback_url"] = config_update.callback_url

        if updates:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.patch(
                    f"{NANGO_API_BASE}/environment",
                    headers=get_nango_headers(),
                    json=updates
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Nango API error: {response.text}"
                    )

        return APIResponse(
            success=True,
            data={"message": "Configuration updated successfully", "updates": updates},
            meta=get_response_meta()
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to update Nango configuration: {str(e)}"
        )


# === Provider Catalog ===

@router.get("/providers")
async def list_providers(
    user: UserContext = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    auth_mode: Optional[NangoAuthType] = Query(None, description="Filter by auth type")
) -> APIResponse:
    """
    List available Nango providers.

    Returns the catalog of 500+ supported API providers that can be integrated.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/providers",
                headers=get_nango_headers()
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()
            providers = data.get("providers", [])

            # Apply filters
            if search:
                search_lower = search.lower()
                providers = [p for p in providers
                           if search_lower in p.get("unique_key", "").lower()
                           or search_lower in p.get("display_name", "").lower()]

            if category:
                providers = [p for p in providers
                           if category.lower() in [c.lower() for c in p.get("categories", [])]]

            if auth_mode:
                providers = [p for p in providers
                           if p.get("auth_mode", "").upper() == auth_mode.value]

            provider_list = [
                NangoProviderInfo(
                    unique_key=p.get("unique_key", ""),
                    display_name=p.get("display_name", p.get("unique_key", "")),
                    auth_mode=NangoAuthType(p.get("auth_mode", "OAUTH2").upper())
                              if p.get("auth_mode") else NangoAuthType.OAUTH2,
                    docs=p.get("docs"),
                    categories=p.get("categories", []),
                    scopes=p.get("default_scopes", [])
                )
                for p in providers
            ]

            return APIResponse(
                success=True,
                data=NangoProviderListResponse(
                    providers=provider_list,
                    total=len(provider_list)
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch Nango providers: {str(e)}"
        )


@router.get("/providers/{provider_key}")
async def get_provider(
    provider_key: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Get details for a specific provider.

    Returns full configuration options, scopes, and documentation for a provider.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/providers/{provider_key}",
                headers=get_nango_headers()
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Provider '{provider_key}' not found"
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data=response.json(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch provider details: {str(e)}"
        )


# === Integration Management ===

@router.get("/integrations")
async def list_integrations(
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    List configured integrations.

    Returns integrations that have been set up in the Nango environment
    with their sync and action configurations.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/integrations",
                headers=get_nango_headers()
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()
            integrations = [
                NangoIntegrationConfig(
                    unique_key=i.get("unique_key", ""),
                    provider=i.get("provider", ""),
                    created_at=i.get("created_at"),
                    syncs=i.get("syncs", []),
                    actions=i.get("actions", []),
                    webhook_url=i.get("webhook_url"),
                    is_active=i.get("is_active", True)
                )
                for i in data.get("integrations", [])
            ]

            return APIResponse(
                success=True,
                data=NangoIntegrationListResponse(
                    integrations=integrations,
                    total=len(integrations)
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch integrations: {str(e)}"
        )


@router.get("/integrations/{integration_key}")
async def get_integration(
    integration_key: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Get details for a specific integration.

    Returns full configuration including syncs, actions, and connection count.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/integrations/{integration_key}",
                headers=get_nango_headers()
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Integration '{integration_key}' not found"
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data=response.json(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch integration details: {str(e)}"
        )


# === Connection Management ===

@router.get("/connections")
async def list_connections(
    user: UserContext = Depends(get_current_user),
    integration_key: Optional[str] = Query(None, description="Filter by integration"),
    connection_status: Optional[NangoConnectionStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=500, description="Items per page")
) -> APIResponse:
    """
    List all connections.

    Returns OAuth and API key connections with their status and metadata.
    """
    try:
        params = {"limit": limit, "offset": (page - 1) * limit}
        if integration_key:
            params["integration_id"] = integration_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/connections",
                headers=get_nango_headers(),
                params=params
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()
            connections = []

            for c in data.get("connections", []):
                conn_status = NangoConnectionStatus.ACTIVE
                if c.get("credentials", {}).get("expires_at"):
                    expires = datetime.fromisoformat(c["credentials"]["expires_at"].replace("Z", "+00:00"))
                    if expires < datetime.now(PACIFIC):
                        conn_status = NangoConnectionStatus.EXPIRED
                if c.get("error"):
                    conn_status = NangoConnectionStatus.ERROR

                if connection_status and conn_status != connection_status:
                    continue

                connections.append(NangoConnection(
                    id=c.get("id", ""),
                    connection_id=c.get("connection_id", ""),
                    provider_config_key=c.get("provider_config_key", ""),
                    provider=c.get("provider", ""),
                    environment_id=c.get("environment_id", ""),
                    status=conn_status,
                    created_at=datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
                              if c.get("created_at") else datetime.now(PACIFIC),
                    updated_at=datetime.fromisoformat(c["updated_at"].replace("Z", "+00:00"))
                              if c.get("updated_at") else None,
                    last_fetched_at=datetime.fromisoformat(c["last_fetched_at"].replace("Z", "+00:00"))
                                   if c.get("last_fetched_at") else None,
                    connection_config=c.get("connection_config", {}),
                    metadata=c.get("metadata", {}),
                    end_user=c.get("end_user")
                ))

            return APIResponse(
                success=True,
                data=NangoConnectionListResponse(
                    connections=connections,
                    total=data.get("total", len(connections)),
                    page=page,
                    has_more=len(data.get("connections", [])) >= limit
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch connections: {str(e)}"
        )


@router.get("/connections/{connection_id}")
async def get_connection(
    connection_id: str,
    user: UserContext = Depends(get_current_user),
    provider_config_key: Optional[str] = Query(None, description="Integration key")
) -> APIResponse:
    """
    Get details for a specific connection.

    Returns connection status, credentials (masked), and metadata.
    """
    try:
        params = {}
        if provider_config_key:
            params["provider_config_key"] = provider_config_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/connection/{connection_id}",
                headers=get_nango_headers(),
                params=params
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Connection '{connection_id}' not found"
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data=response.json(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch connection details: {str(e)}"
        )


@router.post("/connections/oauth/connect")
async def initiate_oauth(
    user: UserContext = Depends(get_current_user),
    integration_key: str = Query(..., description="Integration to connect"),
    connection_id: str = Query(..., description="Unique connection identifier"),
    user_scopes: Optional[str] = Query(None, description="Comma-separated OAuth scopes")
) -> APIResponse:
    """
    Initiate OAuth connection flow.

    Returns the OAuth authorization URL to redirect the user to.
    Frontend should redirect user to this URL to complete OAuth.
    """
    public_key = get_nango_public_key()
    if not public_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nango public key not configured. Set NANGO_PUBLIC_KEY environment variable."
        )

    callback_url = os.environ.get("NANGO_CALLBACK_URL", "")

    # Build OAuth URL
    auth_url = f"{NANGO_API_BASE.replace('/api', '')}/oauth/connect/{integration_key}"
    params = {
        "public_key": public_key,
        "connection_id": connection_id
    }
    if callback_url:
        params["callback_url"] = callback_url
    if user_scopes:
        params["user_scopes"] = user_scopes

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    full_auth_url = f"{auth_url}?{query_string}"

    return APIResponse(
        success=True,
        data=OAuthConnectResponse(
            auth_url=full_auth_url,
            state=connection_id,
            provider=integration_key
        ).model_dump(),
        meta=get_response_meta()
    )


@router.post("/connections")
async def create_connection(
    connection_request: CreateConnectionRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Create a connection with API key or basic auth.

    For OAuth connections, use the /oauth/connect endpoint instead.
    """
    try:
        payload = {
            "provider_config_key": connection_request.provider_config_key,
            "connection_id": connection_request.connection_id,
            "credentials": connection_request.credentials,
            "connection_config": connection_request.connection_config,
            "metadata": connection_request.metadata
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{NANGO_API_BASE}/connection",
                headers=get_nango_headers(),
                json=payload
            )

            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data=response.json(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to create connection: {str(e)}"
        )


@router.delete("/connections/{connection_id}")
async def delete_connection(
    connection_id: str,
    user: UserContext = Depends(get_current_user),
    provider_config_key: Optional[str] = Query(None, description="Integration key")
) -> APIResponse:
    """
    Delete a connection.

    Revokes tokens and removes the connection from Nango.
    """
    try:
        params = {}
        if provider_config_key:
            params["provider_config_key"] = provider_config_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(
                f"{NANGO_API_BASE}/connection/{connection_id}",
                headers=get_nango_headers(),
                params=params
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Connection '{connection_id}' not found"
                )

            if response.status_code not in (200, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data={"message": f"Connection '{connection_id}' deleted successfully"},
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to delete connection: {str(e)}"
        )


@router.get("/connections/{connection_id}/token")
async def get_connection_token(
    connection_id: str,
    user: UserContext = Depends(get_current_user),
    provider_config_key: Optional[str] = Query(None, description="Integration key")
) -> APIResponse:
    """
    Get access token for a connection.

    Returns a fresh access token, automatically refreshing if needed.
    Use this when you need to make direct API calls to the provider.
    """
    try:
        params = {}
        if provider_config_key:
            params["provider_config_key"] = provider_config_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/connection/{connection_id}",
                headers=get_nango_headers(),
                params=params
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Connection '{connection_id}' not found"
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()
            credentials = data.get("credentials", {})

            token_response = ConnectionTokenResponse(
                connection_id=connection_id,
                provider=data.get("provider", ""),
                access_token=credentials.get("access_token", ""),
                expires_at=datetime.fromisoformat(credentials["expires_at"].replace("Z", "+00:00"))
                          if credentials.get("expires_at") else None,
                refresh_token=credentials.get("refresh_token")
            )

            return APIResponse(
                success=True,
                data=token_response.model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch connection token: {str(e)}"
        )


@router.patch("/connections/{connection_id}/metadata")
async def update_connection_metadata(
    connection_id: str,
    metadata: Dict[str, Any],
    user: UserContext = Depends(get_current_user),
    provider_config_key: Optional[str] = Query(None, description="Integration key")
) -> APIResponse:
    """
    Update metadata for a connection.

    Metadata is merged with existing metadata (not replaced).
    """
    try:
        params = {}
        if provider_config_key:
            params["provider_config_key"] = provider_config_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                f"{NANGO_API_BASE}/connection/{connection_id}/metadata",
                headers=get_nango_headers(),
                params=params,
                json=metadata
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Connection '{connection_id}' not found"
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data=response.json(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to update connection metadata: {str(e)}"
        )


# === Sync Management ===

@router.get("/syncs/{connection_id}")
async def list_syncs(
    connection_id: str,
    user: UserContext = Depends(get_current_user),
    provider_config_key: Optional[str] = Query(None, description="Integration key")
) -> APIResponse:
    """
    List syncs for a connection.

    Returns configured syncs with their status and last run info.
    """
    try:
        params = {}
        if provider_config_key:
            params["provider_config_key"] = provider_config_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/sync/status",
                headers=get_nango_headers(),
                params={**params, "connection_id": connection_id}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data=response.json(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch syncs: {str(e)}"
        )


@router.post("/syncs/trigger")
async def trigger_sync(
    sync_request: TriggerSyncRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Trigger a sync manually.

    Starts a sync immediately, optionally as a full resync.
    """
    try:
        payload = {
            "connection_id": sync_request.connection_id,
            "sync_name": sync_request.sync_name,
            "full_resync": sync_request.full_resync
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{NANGO_API_BASE}/sync/trigger",
                headers=get_nango_headers(),
                json=payload
            )

            if response.status_code not in (200, 202):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()

            return APIResponse(
                success=True,
                data=TriggerSyncResponse(
                    success=True,
                    sync_id=data.get("sync_id", ""),
                    run_id=data.get("run_id"),
                    message="Sync triggered successfully"
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to trigger sync: {str(e)}"
        )


@router.post("/syncs/pause")
async def pause_sync(
    connection_id: str = Query(..., description="Connection ID"),
    sync_name: str = Query(..., description="Sync name"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Pause a sync.

    Stops automatic sync runs until resumed.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{NANGO_API_BASE}/sync/pause",
                headers=get_nango_headers(),
                json={"connection_id": connection_id, "sync_name": sync_name}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data={"message": f"Sync '{sync_name}' paused successfully"},
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to pause sync: {str(e)}"
        )


@router.post("/syncs/start")
async def start_sync(
    connection_id: str = Query(..., description="Connection ID"),
    sync_name: str = Query(..., description="Sync name"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Resume a paused sync.

    Restarts automatic sync runs.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{NANGO_API_BASE}/sync/start",
                headers=get_nango_headers(),
                json={"connection_id": connection_id, "sync_name": sync_name}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            return APIResponse(
                success=True,
                data={"message": f"Sync '{sync_name}' started successfully"},
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to start sync: {str(e)}"
        )


@router.get("/syncs/{connection_id}/records")
async def get_sync_records(
    connection_id: str,
    model: str = Query(..., description="Sync model name"),
    user: UserContext = Depends(get_current_user),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(100, ge=1, le=1000, description="Records per page"),
    modified_after: Optional[str] = Query(None, description="ISO timestamp filter")
) -> APIResponse:
    """
    Get records from a sync.

    Returns synced data for a specific model with pagination.
    """
    try:
        params = {
            "model": model,
            "limit": limit
        }
        if cursor:
            params["cursor"] = cursor
        if modified_after:
            params["modified_after"] = modified_after

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/sync/records",
                headers=get_nango_headers(),
                params={**params, "connection_id": connection_id}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()

            return APIResponse(
                success=True,
                data=SyncRecordsResponse(
                    records=data.get("records", []),
                    next_cursor=data.get("next_cursor"),
                    total=data.get("total")
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch sync records: {str(e)}"
        )


# === Action Execution ===

@router.post("/actions/trigger")
async def trigger_action(
    action_request: ActionTriggerRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Trigger an action.

    Executes an integration action (like creating a resource) and returns the result.
    """
    try:
        payload = {
            "connection_id": action_request.connection_id,
            "input": action_request.input
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{NANGO_API_BASE}/action/trigger",
                headers=get_nango_headers(),
                params={"action_name": action_request.action_name},
                json=payload
            )

            data = response.json() if response.content else {}

            if response.status_code not in (200, 201):
                return APIResponse(
                    success=False,
                    data=ActionTriggerResponse(
                        success=False,
                        action_name=action_request.action_name,
                        output=None,
                        error=data.get("error", response.text)
                    ).model_dump(),
                    meta=get_response_meta()
                )

            return APIResponse(
                success=True,
                data=ActionTriggerResponse(
                    success=True,
                    action_name=action_request.action_name,
                    output=data,
                    error=None
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to trigger action: {str(e)}"
        )


# === Webhooks ===

@router.post("/webhooks/receive")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> APIResponse:
    """
    Receive webhooks from Nango.

    Handles sync completion, auth events, and forwarded webhooks.
    """
    try:
        # Verify webhook signature if configured
        signature = request.headers.get("X-Nango-Signature")
        webhook_secret = os.environ.get("NANGO_WEBHOOK_SECRET", "")

        body = await request.body()
        payload = json.loads(body)

        # TODO: Verify signature using HMAC
        # if webhook_secret and signature:
        #     expected = hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        #     if not hmac.compare_digest(signature, expected):
        #         raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse event
        event_type = payload.get("type", "unknown")
        connection_id = payload.get("connection_id", "")

        logger.info(f"Received Nango webhook: {event_type} for {connection_id}")

        # Queue processing in background
        async def process_webhook():
            # Handle different event types
            if event_type == "sync":
                sync_name = payload.get("sync_name")
                sync_type = payload.get("sync_type")
                success = payload.get("success", True)
                logger.info(f"Sync {sync_name} completed: success={success}")
            elif event_type == "auth":
                operation = payload.get("operation")
                logger.info(f"Auth event: {operation} for {connection_id}")
            elif event_type == "forward":
                # Forwarded webhook from provider
                provider_event = payload.get("payload", {})
                logger.info(f"Forwarded webhook from provider: {provider_event.get('type')}")

        background_tasks.add_task(process_webhook)

        return APIResponse(
            success=True,
            data={"received": True, "type": event_type},
            meta=get_response_meta()
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


# === Logs ===

@router.get("/logs")
async def get_logs(
    user: UserContext = Depends(get_current_user),
    connection_id: Optional[str] = Query(None, description="Filter by connection"),
    level: Optional[str] = Query(None, description="Filter by level (info, warn, error)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs"),
    cursor: Optional[str] = Query(None, description="Pagination cursor")
) -> APIResponse:
    """
    Get Nango operation logs.

    Returns logs for debugging syncs, actions, and auth flows.
    """
    try:
        params = {"limit": limit}
        if connection_id:
            params["connection_id"] = connection_id
        if level:
            params["level"] = level
        if cursor:
            params["cursor"] = cursor

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/logs/operations",
                headers=get_nango_headers(),
                params=params
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nango API error: {response.text}"
                )

            data = response.json()

            logs = [
                NangoLogEntry(
                    id=log.get("id", ""),
                    level=log.get("level", "info"),
                    type=log.get("type", ""),
                    message=log.get("message", ""),
                    connection_id=log.get("connection_id"),
                    sync_name=log.get("sync_name"),
                    action_name=log.get("action_name"),
                    timestamp=datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
                              if log.get("timestamp") else datetime.now(PACIFIC),
                    metadata=log.get("metadata", {})
                )
                for log in data.get("logs", [])
            ]

            return APIResponse(
                success=True,
                data=NangoLogListResponse(
                    logs=logs,
                    cursor=data.get("cursor"),
                    has_more=data.get("has_more", False)
                ).model_dump(),
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch logs: {str(e)}"
        )


# === Health Check ===

@router.get("/health")
async def health_check() -> APIResponse:
    """
    Check Nango service health.

    Verifies connectivity to Nango API.
    """
    secret_key = os.environ.get("NANGO_SECRET_KEY", "")

    if not secret_key:
        return APIResponse(
            success=True,
            data={
                "status": "not_configured",
                "message": "NANGO_SECRET_KEY not set"
            },
            meta=get_response_meta()
        )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{NANGO_API_BASE}/health",
                headers=get_nango_headers()
            )

            is_healthy = response.status_code == 200

            return APIResponse(
                success=True,
                data={
                    "status": "healthy" if is_healthy else "unhealthy",
                    "nango_api": is_healthy,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000)
                },
                meta=get_response_meta()
            )
    except httpx.RequestError as e:
        return APIResponse(
            success=True,
            data={
                "status": "unhealthy",
                "nango_api": False,
                "error": str(e)
            },
            meta=get_response_meta()
        )
