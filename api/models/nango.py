"""
Nango Integration Manager Models

Pydantic models for Nango unified API integration.
Nango provides OAuth management for 500+ APIs with unified connection handling.

Nango API Reference: https://docs.nango.dev/reference/api
"""
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class NangoAuthType(str, Enum):
    """Nango authentication types."""
    OAUTH2 = "OAUTH2"
    OAUTH1 = "OAUTH1"
    API_KEY = "API_KEY"
    BASIC = "BASIC"
    APP = "APP"
    CUSTOM = "CUSTOM"
    TBA = "TBA"  # Token-Based Authentication


class NangoConnectionStatus(str, Enum):
    """Status of a Nango connection."""
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"


class NangoSyncStatus(str, Enum):
    """Status of a Nango sync."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    SUCCESS = "success"
    ERROR = "error"


class NangoSyncType(str, Enum):
    """Type of sync operation."""
    FULL = "full"
    INCREMENTAL = "incremental"


# === Integration Definitions ===

class NangoIntegrationProvider(BaseModel):
    """A Nango integration provider definition."""
    unique_key: str = Field(..., description="Unique provider key (e.g., 'google')")
    display_name: str = Field(..., description="Display name")
    logo: Optional[str] = Field(None, description="Logo URL")
    auth_mode: NangoAuthType = Field(..., description="Authentication type")
    categories: List[str] = Field(default_factory=list, description="Integration categories")
    docs_url: Optional[str] = Field(None, description="Documentation URL")


class NangoIntegrationConfig(BaseModel):
    """Configuration for an integration."""
    unique_key: str = Field(..., description="Integration unique key")
    provider: str = Field(..., description="Provider unique key")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    syncs: List[str] = Field(default_factory=list, description="Configured sync names")
    actions: List[str] = Field(default_factory=list, description="Available action names")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for this integration")
    is_active: bool = Field(default=True, description="Whether integration is active")


class NangoIntegrationListResponse(BaseModel):
    """Response listing available integrations."""
    integrations: List[NangoIntegrationConfig] = Field(..., description="List of integrations")
    total: int = Field(..., description="Total count")


# === Connection Management ===

class NangoConnectionCredentials(BaseModel):
    """Credentials stored for a connection."""
    type: NangoAuthType = Field(..., description="Credential type")
    access_token: Optional[str] = Field(None, description="OAuth access token (masked)")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token (masked)")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    raw: Dict[str, Any] = Field(default_factory=dict, description="Raw credential data")


class NangoConnection(BaseModel):
    """A Nango connection to an external API."""
    id: str = Field(..., description="Connection ID")
    connection_id: str = Field(..., description="User-provided connection identifier")
    provider_config_key: str = Field(..., description="Integration config key")
    provider: str = Field(..., description="Provider name")
    environment_id: str = Field(..., description="Environment ID")
    status: NangoConnectionStatus = Field(default=NangoConnectionStatus.ACTIVE, description="Connection status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_fetched_at: Optional[datetime] = Field(None, description="Last credential fetch time")
    credentials: Optional[NangoConnectionCredentials] = Field(None, description="Connection credentials")
    connection_config: Dict[str, Any] = Field(default_factory=dict, description="Connection-specific config")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="User metadata")
    end_user: Optional[Dict[str, Any]] = Field(None, description="End user info")


class NangoConnectionListResponse(BaseModel):
    """Response listing connections."""
    connections: List[NangoConnection] = Field(..., description="List of connections")
    total: int = Field(..., description="Total count")
    page: int = Field(default=1, description="Current page")
    has_more: bool = Field(default=False, description="More pages available")


class CreateConnectionRequest(BaseModel):
    """Request to create a connection via API key or basic auth."""
    provider_config_key: str = Field(..., description="Integration config key")
    connection_id: str = Field(..., description="Unique connection identifier")
    credentials: Dict[str, Any] = Field(..., description="Credentials (api_key, username/password, etc.)")
    connection_config: Dict[str, Any] = Field(default_factory=dict, description="Additional config")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="User metadata")


class OAuthConnectResponse(BaseModel):
    """Response for OAuth connection initiation."""
    auth_url: str = Field(..., description="OAuth authorization URL")
    state: str = Field(..., description="State parameter for OAuth")
    provider: str = Field(..., description="Provider name")


class ConnectionTokenResponse(BaseModel):
    """Response with connection access token."""
    connection_id: str = Field(..., description="Connection identifier")
    provider: str = Field(..., description="Provider name")
    access_token: str = Field(..., description="Access token")
    expires_at: Optional[datetime] = Field(None, description="Token expiration")
    refresh_token: Optional[str] = Field(None, description="Refresh token if available")


# === Sync Management ===

class NangoSyncRecord(BaseModel):
    """A record from a sync operation."""
    id: str = Field(..., description="Record ID")
    model: str = Field(..., description="Model/sync name")
    data: Dict[str, Any] = Field(..., description="Record data")
    created_at: datetime = Field(..., description="Record creation time")
    updated_at: Optional[datetime] = Field(None, description="Record update time")
    deleted_at: Optional[datetime] = Field(None, description="Record deletion time (soft delete)")


class NangoSyncRun(BaseModel):
    """A sync run/execution."""
    id: str = Field(..., description="Sync run ID")
    sync_id: str = Field(..., description="Sync configuration ID")
    sync_name: str = Field(..., description="Sync name")
    connection_id: str = Field(..., description="Connection ID")
    status: NangoSyncStatus = Field(..., description="Run status")
    type: NangoSyncType = Field(default=NangoSyncType.INCREMENTAL, description="Sync type")
    started_at: datetime = Field(..., description="Run start time")
    ended_at: Optional[datetime] = Field(None, description="Run end time")
    result: Optional[Dict[str, Any]] = Field(None, description="Run result/stats")
    error: Optional[str] = Field(None, description="Error message if failed")
    records_added: int = Field(default=0, description="Records added")
    records_updated: int = Field(default=0, description="Records updated")
    records_deleted: int = Field(default=0, description="Records deleted")


class NangoSyncRunListResponse(BaseModel):
    """Response listing sync runs."""
    sync_runs: List[NangoSyncRun] = Field(..., description="List of sync runs")
    total: int = Field(..., description="Total count")


class TriggerSyncRequest(BaseModel):
    """Request to trigger a sync."""
    connection_id: str = Field(..., description="Connection ID")
    sync_name: str = Field(..., description="Sync name to trigger")
    full_resync: bool = Field(default=False, description="Whether to do full resync")


class TriggerSyncResponse(BaseModel):
    """Response from triggering a sync."""
    success: bool = Field(..., description="Whether trigger succeeded")
    sync_id: str = Field(..., description="Sync configuration ID")
    run_id: Optional[str] = Field(None, description="New sync run ID")
    message: str = Field(..., description="Status message")


class SyncRecordsRequest(BaseModel):
    """Request to fetch sync records."""
    connection_id: str = Field(..., description="Connection ID")
    model: str = Field(..., description="Model/sync name")
    cursor: Optional[str] = Field(None, description="Pagination cursor")
    limit: int = Field(default=100, ge=1, le=1000, description="Records per page")
    filter: Optional[Dict[str, Any]] = Field(None, description="Optional filter")
    modified_after: Optional[datetime] = Field(None, description="Filter by modification time")


class SyncRecordsResponse(BaseModel):
    """Response with sync records."""
    records: List[Dict[str, Any]] = Field(..., description="Sync records")
    next_cursor: Optional[str] = Field(None, description="Next page cursor")
    total: Optional[int] = Field(None, description="Total records (if available)")


# === Action Execution ===

class ActionTriggerRequest(BaseModel):
    """Request to trigger an action."""
    connection_id: str = Field(..., description="Connection ID")
    action_name: str = Field(..., description="Action name to execute")
    input: Dict[str, Any] = Field(default_factory=dict, description="Action input parameters")


class ActionTriggerResponse(BaseModel):
    """Response from an action execution."""
    success: bool = Field(..., description="Whether action succeeded")
    action_name: str = Field(..., description="Action name")
    output: Optional[Dict[str, Any]] = Field(None, description="Action output")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: Optional[int] = Field(None, description="Execution duration in ms")


# === Webhooks ===

class NangoWebhookType(str, Enum):
    """Types of Nango webhooks."""
    SYNC = "sync"
    AUTH = "auth"
    FORWARD = "forward"


class NangoWebhookEvent(BaseModel):
    """A webhook event from Nango."""
    type: NangoWebhookType = Field(..., description="Webhook type")
    connection_id: str = Field(..., description="Connection ID")
    provider_config_key: str = Field(..., description="Integration config key")
    environment_id: str = Field(..., description="Environment ID")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    timestamp: datetime = Field(..., description="Event timestamp")
    # Sync-specific fields
    sync_name: Optional[str] = Field(None, description="Sync name (for sync webhooks)")
    sync_type: Optional[NangoSyncType] = Field(None, description="Sync type")
    # Auth-specific fields
    auth_mode: Optional[NangoAuthType] = Field(None, description="Auth mode (for auth webhooks)")
    operation: Optional[str] = Field(None, description="Auth operation")


# === Environment & Configuration ===

class NangoEnvironment(BaseModel):
    """A Nango environment (dev/prod)."""
    id: str = Field(..., description="Environment ID")
    name: str = Field(..., description="Environment name")
    secret_key: str = Field(..., description="Secret key (masked)")
    public_key: str = Field(..., description="Public key")
    callback_url: Optional[str] = Field(None, description="OAuth callback URL")
    webhook_url: Optional[str] = Field(None, description="Webhook receive URL")
    created_at: datetime = Field(..., description="Creation timestamp")


class NangoConfigStatus(BaseModel):
    """Nango API configuration status."""
    is_configured: bool = Field(..., description="Whether API key is set")
    is_valid: bool = Field(..., description="Whether API key is valid")
    environment: Optional[str] = Field(None, description="Current environment name")
    base_url: str = Field(..., description="Nango API base URL")
    callback_url: Optional[str] = Field(None, description="OAuth callback URL")
    integrations_count: int = Field(default=0, description="Number of configured integrations")
    connections_count: int = Field(default=0, description="Number of active connections")
    version: Optional[str] = Field(None, description="Nango SDK version")


class UpdateNangoConfigRequest(BaseModel):
    """Request to update Nango configuration."""
    webhook_url: Optional[str] = Field(None, description="Webhook URL to set")
    callback_url: Optional[str] = Field(None, description="OAuth callback URL to set")
    default_connection_config: Optional[Dict[str, Any]] = Field(None, description="Default connection config")


# === Provider Catalog ===

class NangoProviderInfo(BaseModel):
    """Information about a supported provider."""
    unique_key: str = Field(..., description="Provider unique key")
    display_name: str = Field(..., description="Display name")
    auth_mode: NangoAuthType = Field(..., description="Authentication type")
    docs: Optional[str] = Field(None, description="Documentation URL")
    categories: List[str] = Field(default_factory=list, description="Categories")
    scopes: List[str] = Field(default_factory=list, description="Default OAuth scopes")


class NangoProviderListResponse(BaseModel):
    """Response listing available providers."""
    providers: List[NangoProviderInfo] = Field(..., description="Available providers")
    total: int = Field(..., description="Total count")


# === Logs ===

class NangoLogEntry(BaseModel):
    """A Nango log entry."""
    id: str = Field(..., description="Log entry ID")
    level: str = Field(..., description="Log level (info, warn, error)")
    type: str = Field(..., description="Log type")
    message: str = Field(..., description="Log message")
    connection_id: Optional[str] = Field(None, description="Related connection ID")
    sync_name: Optional[str] = Field(None, description="Related sync name")
    action_name: Optional[str] = Field(None, description="Related action name")
    timestamp: datetime = Field(..., description="Log timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class NangoLogListResponse(BaseModel):
    """Response listing logs."""
    logs: List[NangoLogEntry] = Field(..., description="Log entries")
    cursor: Optional[str] = Field(None, description="Next page cursor")
    has_more: bool = Field(default=False, description="More logs available")
