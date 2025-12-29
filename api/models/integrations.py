"""
Integrations Hub Models

Pydantic models for centralized integration management.
Supports OAuth integrations, API key integrations, and MCP connections.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IntegrationType(str, Enum):
    """Type of integration connection method."""
    OAUTH = "oauth"
    API_KEY = "api_key"
    MCP = "mcp"
    SKILL = "skill"


class IntegrationCategory(str, Enum):
    """Categories of integrations."""
    EMAIL = "email"
    CALENDAR = "calendar"
    STORAGE = "storage"
    PROJECT_MANAGEMENT = "project_management"
    COMMUNICATION = "communication"
    CRM = "crm"
    ERP = "erp"
    DATABASE = "database"
    CONTENT = "content"
    AI = "ai"
    OTHER = "other"


class ConnectionStatus(str, Enum):
    """Status of an integration connection."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"


class SyncFrequency(str, Enum):
    """How often to sync data."""
    REALTIME = "realtime"
    MINUTES_5 = "5m"
    MINUTES_15 = "15m"
    MINUTES_30 = "30m"
    HOURLY = "1h"
    DAILY = "24h"
    MANUAL = "manual"


# === Integration Definition (Static catalog) ===

class IntegrationCapability(BaseModel):
    """What an integration can do."""
    read: bool = Field(default=False, description="Can read data")
    write: bool = Field(default=False, description="Can write data")
    sync: bool = Field(default=False, description="Supports auto-sync")
    webhook: bool = Field(default=False, description="Supports webhooks")
    realtime: bool = Field(default=False, description="Supports realtime updates")


class IntegrationDefinition(BaseModel):
    """Static definition of an available integration."""
    id: str = Field(..., description="Unique integration identifier (e.g., 'gmail', 'clickup')")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="What this integration does")
    category: IntegrationCategory = Field(..., description="Integration category")
    type: IntegrationType = Field(..., description="Connection method")
    icon_url: Optional[str] = Field(None, description="Icon URL for UI")
    docs_url: Optional[str] = Field(None, description="Documentation URL")
    capabilities: IntegrationCapability = Field(
        default_factory=IntegrationCapability,
        description="What this integration can do"
    )
    required_scopes: List[str] = Field(
        default_factory=list,
        description="OAuth scopes or permissions required"
    )
    is_premium: bool = Field(default=False, description="Requires premium subscription")
    is_beta: bool = Field(default=False, description="Integration is in beta")


# === User Connection (Per-user state) ===

class IntegrationConnection(BaseModel):
    """A user's connection to an integration."""
    integration_id: str = Field(..., description="Integration ID from catalog")
    user_id: str = Field(..., description="User who connected")
    workspace_id: str = Field(..., description="Workspace this connection belongs to")
    status: ConnectionStatus = Field(..., description="Current connection status")
    connected_at: Optional[datetime] = Field(None, description="When connected")
    last_sync: Optional[datetime] = Field(None, description="Last successful sync")
    sync_frequency: SyncFrequency = Field(
        default=SyncFrequency.MANUAL,
        description="How often to auto-sync"
    )
    settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Integration-specific settings"
    )
    error_message: Optional[str] = Field(None, description="Last error if any")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class IntegrationWithConnection(BaseModel):
    """Integration definition with user's connection status."""
    integration: IntegrationDefinition
    connection: Optional[IntegrationConnection] = None
    is_connected: bool = Field(default=False, description="Whether user has connected")


# === Request/Response Models ===

class IntegrationListResponse(BaseModel):
    """List of integrations with connection status."""
    integrations: List[IntegrationWithConnection]
    total: int = Field(..., description="Total number of integrations")
    connected_count: int = Field(default=0, description="Number connected")


class IntegrationDetailResponse(BaseModel):
    """Detailed integration info."""
    integration: IntegrationDefinition
    connection: Optional[IntegrationConnection] = None
    recent_logs: List["SyncLogEntry"] = Field(
        default_factory=list,
        description="Recent sync activity"
    )


class OAuthInitiateResponse(BaseModel):
    """Response when starting OAuth flow."""
    auth_url: str = Field(..., description="URL to redirect user for authorization")
    state: str = Field(..., description="OAuth state token")
    expires_at: str = Field(..., description="When the state expires")


class OAuthCallbackRequest(BaseModel):
    """OAuth callback parameters."""
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State token to verify")


class DisconnectResponse(BaseModel):
    """Response after disconnecting an integration."""
    success: bool = Field(..., description="Whether disconnect succeeded")
    integration_id: str = Field(..., description="Integration that was disconnected")
    message: str = Field(..., description="Status message")


class HealthCheckResponse(BaseModel):
    """Response for integration health check."""
    integration_id: str = Field(..., description="Integration ID")
    status: ConnectionStatus = Field(..., description="Current status")
    is_healthy: bool = Field(..., description="Whether connection is working")
    last_check: str = Field(..., description="When health was checked")
    token_expires_in: Optional[int] = Field(
        None,
        description="Seconds until token expires"
    )
    error: Optional[str] = Field(None, description="Error if unhealthy")


class SyncTriggerRequest(BaseModel):
    """Request to trigger a manual sync."""
    full_sync: bool = Field(
        default=False,
        description="Full sync vs incremental"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Integration-specific sync options"
    )


class SyncTriggerResponse(BaseModel):
    """Response after triggering sync."""
    integration_id: str = Field(..., description="Integration ID")
    sync_id: str = Field(..., description="ID for tracking this sync")
    status: str = Field(..., description="Sync status (queued, running, etc.)")
    estimated_duration: Optional[int] = Field(
        None,
        description="Estimated seconds to complete"
    )


class SyncLogEntry(BaseModel):
    """A single sync log entry."""
    id: str = Field(..., description="Log entry ID")
    timestamp: str = Field(..., description="When this happened")
    action: str = Field(..., description="What happened (sync, error, etc.)")
    status: str = Field(..., description="Success, failure, etc.")
    items_processed: int = Field(default=0, description="Number of items processed")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    error: Optional[str] = Field(None, description="Error message if failed")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional details"
    )


class SyncLogsResponse(BaseModel):
    """Paginated sync logs."""
    logs: List[SyncLogEntry]
    total: int = Field(..., description="Total log entries")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=20, description="Items per page")
    has_more: bool = Field(default=False, description="More pages available")


class UpdateSettingsRequest(BaseModel):
    """Request to update integration settings."""
    sync_frequency: Optional[SyncFrequency] = Field(
        None,
        description="New sync frequency"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Integration-specific settings to update"
    )
