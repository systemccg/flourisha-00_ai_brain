"""
Mobile App API Models

Pydantic models for React Native mobile app endpoints.
Optimized for mobile use cases: offline-first, minimal payloads, push notifications.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# === Enums ===

class DevicePlatform(str, Enum):
    """Supported mobile platforms."""
    IOS = "ios"
    ANDROID = "android"


class ContentType(str, Enum):
    """Types of mobile captures."""
    VOICE_NOTE = "voice_note"
    PHOTO = "photo"
    TEXT_NOTE = "text_note"
    QUICK_IDEA = "quick_idea"
    BOOKMARK = "bookmark"
    LOCATION = "location"


class NotificationType(str, Enum):
    """Types of push notifications."""
    ENERGY_REMINDER = "energy_reminder"
    TASK_DUE = "task_due"
    MORNING_REPORT = "morning_report"
    OKR_UPDATE = "okr_update"
    SYNC_REMINDER = "sync_reminder"
    SYSTEM_ALERT = "system_alert"


# === Device Registration ===

class DeviceRegistrationRequest(BaseModel):
    """Request to register a mobile device."""
    device_id: str = Field(..., description="Unique device identifier")
    platform: DevicePlatform = Field(..., description="Device platform (ios/android)")
    push_token: Optional[str] = Field(None, description="FCM/APNS push notification token")
    device_name: Optional[str] = Field(None, description="User-friendly device name")
    app_version: str = Field(..., description="App version string")
    os_version: str = Field(..., description="OS version string")
    timezone: str = Field(default="America/Los_Angeles", description="Device timezone")

    model_config = {
        "json_schema_extra": {
            "example": {
                "device_id": "device_abc123",
                "platform": "ios",
                "push_token": "fcm_token_here",
                "device_name": "Greg's iPhone",
                "app_version": "1.0.0",
                "os_version": "17.2",
                "timezone": "America/Los_Angeles"
            }
        }
    }


class DeviceRegistrationResponse(BaseModel):
    """Response after device registration."""
    registration_id: str = Field(..., description="Server-side registration ID")
    features_enabled: List[str] = Field(default_factory=list, description="Enabled features for this device")
    sync_interval_seconds: int = Field(default=300, description="Recommended sync interval")
    push_enabled: bool = Field(default=False, description="Whether push notifications are enabled")


# === Quick Capture ===

class MobileCaptureRequest(BaseModel):
    """Request to capture content from mobile app."""
    content_type: ContentType = Field(..., description="Type of capture")
    content: str = Field(..., description="Text content or base64 for binary")
    title: Optional[str] = Field(None, description="Optional title")
    tags: List[str] = Field(default_factory=list, description="Tags to apply")
    location: Optional[Dict[str, float]] = Field(
        None,
        description="Location data: {lat, lng, accuracy}"
    )
    offline_id: Optional[str] = Field(
        None,
        description="Client-generated ID for offline-first sync"
    )
    captured_at: Optional[str] = Field(
        None,
        description="ISO timestamp when captured (for offline captures)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "content_type": "quick_idea",
                "content": "Feature idea: Add voice transcription to mobile app",
                "tags": ["ideas", "mobile"],
                "offline_id": "offline_123"
            }
        }
    }


class MobileCaptureResponse(BaseModel):
    """Response after mobile capture."""
    capture_id: str = Field(..., description="Server-generated capture ID")
    offline_id: Optional[str] = Field(None, description="Client offline ID (for reconciliation)")
    stored_in: str = Field(..., description="Storage location: 'scratchpad', 'clickup', 'knowledge'")
    clickup_task_id: Optional[str] = Field(None, description="ClickUp task ID if created")
    synced_at: str = Field(..., description="Server sync timestamp")


# === Offline Sync ===

class SyncItem(BaseModel):
    """Item to sync from mobile to server."""
    type: str = Field(..., description="Item type: 'capture', 'energy', 'task_update'")
    offline_id: str = Field(..., description="Client-generated offline ID")
    data: Dict[str, Any] = Field(..., description="Item data")
    created_at: str = Field(..., description="Client timestamp when created")


class MobileSyncRequest(BaseModel):
    """Request to sync offline data to server."""
    device_id: str = Field(..., description="Device identifier")
    last_sync: Optional[str] = Field(None, description="ISO timestamp of last successful sync")
    items_to_upload: List[SyncItem] = Field(default_factory=list, description="Items to upload")
    request_full_sync: bool = Field(default=False, description="Request full data sync")

    model_config = {
        "json_schema_extra": {
            "example": {
                "device_id": "device_abc123",
                "last_sync": "2025-12-29T10:00:00-08:00",
                "items_to_upload": [
                    {
                        "type": "capture",
                        "offline_id": "offline_456",
                        "data": {"content_type": "text_note", "content": "Remember to..."},
                        "created_at": "2025-12-29T09:55:00-08:00"
                    }
                ]
            }
        }
    }


class SyncResult(BaseModel):
    """Result for a single sync item."""
    offline_id: str = Field(..., description="Original offline ID")
    server_id: str = Field(..., description="Server-generated ID")
    success: bool = Field(..., description="Whether sync succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


class MobileSyncResponse(BaseModel):
    """Response with sync results."""
    synced_at: str = Field(..., description="Server sync timestamp")
    upload_results: List[SyncResult] = Field(default_factory=list, description="Results for uploaded items")
    pending_notifications: List[Dict[str, Any]] = Field(default_factory=list, description="Notifications for device")
    active_okr: Optional[Dict[str, Any]] = Field(None, description="Current active OKR summary")
    energy_reminder_due: bool = Field(default=False, description="Whether energy check is due")
    has_more_data: bool = Field(default=False, description="Whether more data available (pagination)")


# === Dashboard Data ===

class DashboardRequest(BaseModel):
    """Request for mobile dashboard data."""
    include_okrs: bool = Field(default=True, description="Include OKR data")
    include_tasks: bool = Field(default=True, description="Include task summary")
    include_energy: bool = Field(default=True, description="Include energy history")
    include_quick_actions: bool = Field(default=True, description="Include quick action buttons")
    limit_tasks: int = Field(default=5, ge=1, le=20, description="Max tasks to return")


class QuickActionButton(BaseModel):
    """Quick action button for mobile home screen."""
    id: str = Field(..., description="Action ID")
    label: str = Field(..., description="Button label")
    icon: str = Field(..., description="Icon name (from app icon set)")
    action_type: str = Field(..., description="Action type: 'capture', 'navigate', 'external'")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action parameters")
    badge_count: int = Field(default=0, description="Badge count to show")


class OKRSummary(BaseModel):
    """Compact OKR summary for mobile."""
    id: str = Field(..., description="OKR ID")
    objective: str = Field(..., description="Objective title")
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    key_results_total: int = Field(..., description="Total key results")
    key_results_completed: int = Field(..., description="Completed key results")
    quarter: str = Field(..., description="Quarter (e.g., 'Q1 2025')")


class TaskSummary(BaseModel):
    """Compact task summary for mobile."""
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    list_name: str = Field(..., description="Parent list name")
    status: str = Field(..., description="Current status")
    priority: Optional[str] = Field(None, description="Priority level")
    due_date: Optional[str] = Field(None, description="Due date if set")


class EnergyEntry(BaseModel):
    """Energy entry for history display."""
    timestamp: str = Field(..., description="Entry timestamp")
    energy_level: int = Field(..., ge=1, le=10, description="Energy level")
    focus_quality: str = Field(..., description="Focus quality")
    current_task: Optional[str] = Field(None, description="Task at time of entry")


class DashboardResponse(BaseModel):
    """Mobile dashboard data response."""
    greeting: str = Field(..., description="Personalized greeting")
    current_date: str = Field(..., description="Current date (Pacific)")
    active_okr: Optional[OKRSummary] = Field(None, description="Active OKR")
    tasks: List[TaskSummary] = Field(default_factory=list, description="Priority tasks")
    energy_history: List[EnergyEntry] = Field(default_factory=list, description="Recent energy entries")
    quick_actions: List[QuickActionButton] = Field(default_factory=list, description="Quick action buttons")
    unread_notifications: int = Field(default=0, description="Unread notification count")
    last_sync: Optional[str] = Field(None, description="Last sync timestamp")


# === Energy Tracking ===

class MobileEnergyRequest(BaseModel):
    """Energy check-in from mobile app."""
    energy_level: int = Field(..., ge=1, le=10, description="Energy level 1-10")
    focus_quality: str = Field(..., description="Focus: 'deep', 'shallow', 'scattered'")
    current_task: Optional[str] = Field(None, description="Current task")
    mood: Optional[str] = Field(None, description="Mood: 'great', 'good', 'okay', 'low'")
    notes: Optional[str] = Field(None, description="Additional notes")
    location: Optional[Dict[str, float]] = Field(None, description="Location if tracking enabled")

    model_config = {
        "json_schema_extra": {
            "example": {
                "energy_level": 7,
                "focus_quality": "deep",
                "current_task": "Writing documentation",
                "mood": "good"
            }
        }
    }


class MobileEnergyResponse(BaseModel):
    """Response after energy check-in."""
    recorded: bool = Field(..., description="Whether entry was recorded")
    entry_id: str = Field(..., description="Entry ID")
    timestamp: str = Field(..., description="Server timestamp")
    next_reminder: Optional[str] = Field(None, description="Next reminder time")
    streak_days: int = Field(default=0, description="Consecutive days of tracking")
    daily_average: Optional[float] = Field(None, description="Today's average energy")


# === Push Notifications ===

class PushNotificationPreferences(BaseModel):
    """User preferences for push notifications."""
    energy_reminders: bool = Field(default=True, description="Receive energy reminders")
    task_reminders: bool = Field(default=True, description="Receive task due reminders")
    morning_report: bool = Field(default=True, description="Receive morning report")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end (HH:MM)")


class UpdatePushPreferencesRequest(BaseModel):
    """Request to update push notification preferences."""
    device_id: str = Field(..., description="Device identifier")
    preferences: PushNotificationPreferences = Field(..., description="New preferences")


class UpdatePushPreferencesResponse(BaseModel):
    """Response after updating preferences."""
    updated: bool = Field(..., description="Whether update succeeded")
    preferences: PushNotificationPreferences = Field(..., description="Current preferences")


# === Voice Notes ===

class VoiceNoteUploadRequest(BaseModel):
    """Request to upload a voice note."""
    audio_data: str = Field(..., description="Base64-encoded audio data")
    duration_seconds: float = Field(..., description="Audio duration in seconds")
    format: str = Field(default="m4a", description="Audio format: 'm4a', 'wav', 'mp3'")
    title: Optional[str] = Field(None, description="Optional title")
    transcribe: bool = Field(default=True, description="Whether to transcribe audio")
    offline_id: Optional[str] = Field(None, description="Offline ID for sync")

    model_config = {
        "json_schema_extra": {
            "example": {
                "audio_data": "base64_audio_data_here...",
                "duration_seconds": 30.5,
                "format": "m4a",
                "transcribe": True
            }
        }
    }


class VoiceNoteUploadResponse(BaseModel):
    """Response after voice note upload."""
    note_id: str = Field(..., description="Voice note ID")
    offline_id: Optional[str] = Field(None, description="Original offline ID")
    status: str = Field(..., description="Status: 'uploaded', 'transcribing', 'complete'")
    transcript: Optional[str] = Field(None, description="Transcript if already available")
    duration_seconds: float = Field(..., description="Confirmed duration")


# === App State ===

class AppStateRequest(BaseModel):
    """Request to get current app state."""
    device_id: str = Field(..., description="Device identifier")
    include_user_profile: bool = Field(default=True, description="Include user profile data")


class UserProfile(BaseModel):
    """User profile for mobile app."""
    uid: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="Display name")
    photo_url: Optional[str] = Field(None, description="Profile photo URL")
    subscription_tier: str = Field(default="free", description="Subscription tier")


class AppStateResponse(BaseModel):
    """Current app state response."""
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[UserProfile] = Field(None, description="User profile if authenticated")
    app_version_supported: bool = Field(default=True, description="Whether app version is supported")
    minimum_app_version: Optional[str] = Field(None, description="Minimum required version")
    maintenance_mode: bool = Field(default=False, description="Whether server is in maintenance")
    maintenance_message: Optional[str] = Field(None, description="Maintenance message if applicable")
    features_enabled: List[str] = Field(default_factory=list, description="Enabled features")
    server_time: str = Field(..., description="Current server time (Pacific)")


# === Search ===

class MobileSearchRequest(BaseModel):
    """Mobile-optimized search request."""
    query: str = Field(..., min_length=2, description="Search query")
    search_type: str = Field(
        default="all",
        description="Search type: 'all', 'tasks', 'knowledge', 'captures'"
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max results")
    include_snippets: bool = Field(default=True, description="Include content snippets")


class SearchResultItem(BaseModel):
    """Single search result for mobile."""
    id: str = Field(..., description="Item ID")
    type: str = Field(..., description="Item type")
    title: str = Field(..., description="Result title")
    snippet: Optional[str] = Field(None, description="Content snippet")
    relevance_score: float = Field(..., description="Relevance score 0-1")
    source: str = Field(..., description="Source: 'clickup', 'knowledge', 'scratchpad'")
    url: Optional[str] = Field(None, description="URL if applicable")
    date: Optional[str] = Field(None, description="Date if applicable")


class MobileSearchResponse(BaseModel):
    """Mobile search response."""
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total matching results")
    results: List[SearchResultItem] = Field(default_factory=list, description="Search results")
    search_time_ms: int = Field(..., description="Search time in milliseconds")
    suggestions: List[str] = Field(default_factory=list, description="Search suggestions")


# === Deep Links ===

class DeepLinkType(str, Enum):
    """Types of deep links."""
    CAPTURE = "capture"
    TASK = "task"
    OKR = "okr"
    SEARCH = "search"
    ENERGY = "energy"
    DASHBOARD = "dashboard"
    PROFILE = "profile"
    SETTINGS = "settings"
    VOICE_NOTE = "voice_note"
    DOCUMENT = "document"
    SHARE = "share"


class DeepLinkParams(BaseModel):
    """Parameters for deep link generation."""
    link_type: DeepLinkType = Field(..., description="Type of deep link")
    target_id: Optional[str] = Field(None, description="Target resource ID (task, capture, etc.)")
    params: Optional[Dict[str, Any]] = Field(None, description="Additional query parameters")
    title: Optional[str] = Field(None, description="Social media title preview")
    description: Optional[str] = Field(None, description="Social media description preview")
    image_url: Optional[str] = Field(None, description="Social media image preview")
    fallback_url: Optional[str] = Field(None, description="Fallback URL for web users")

    model_config = {
        "json_schema_extra": {
            "example": {
                "link_type": "task",
                "target_id": "task_abc123",
                "title": "Check out this task",
                "description": "A task from Flourisha"
            }
        }
    }


class CreateDeepLinkRequest(BaseModel):
    """Request to create a Firebase Dynamic Link."""
    link_params: DeepLinkParams = Field(..., description="Deep link parameters")
    short_link: bool = Field(default=True, description="Generate short link vs long link")
    suffix_option: str = Field(
        default="SHORT",
        description="SHORT (4-char) or UNGUESSABLE (17-char) suffix"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "link_params": {
                    "link_type": "task",
                    "target_id": "task_abc123",
                    "title": "View Task",
                    "description": "Open this task in Flourisha app"
                },
                "short_link": True,
                "suffix_option": "SHORT"
            }
        }
    }


class CreateDeepLinkResponse(BaseModel):
    """Response with generated deep link."""
    short_link: Optional[str] = Field(None, description="Firebase short link URL")
    long_link: str = Field(..., description="Full Firebase Dynamic Link URL")
    preview_link: Optional[str] = Field(None, description="Link preview URL")
    warning: Optional[str] = Field(None, description="Warning message if applicable")
    expires_at: Optional[str] = Field(None, description="Link expiration if set")


class ResolveDeepLinkRequest(BaseModel):
    """Request to resolve a deep link received by the app."""
    link_url: str = Field(..., description="The incoming deep link URL")
    device_id: Optional[str] = Field(None, description="Device ID for attribution")

    model_config = {
        "json_schema_extra": {
            "example": {
                "link_url": "https://flourisha.page.link/abc123",
                "device_id": "device_xyz"
            }
        }
    }


class DeepLinkDestination(BaseModel):
    """Resolved destination for a deep link."""
    screen: str = Field(..., description="Target screen in app")
    params: Dict[str, Any] = Field(default_factory=dict, description="Screen parameters")
    resource_id: Optional[str] = Field(None, description="Resource ID if applicable")
    resource_type: Optional[str] = Field(None, description="Resource type if applicable")
    deferred: bool = Field(default=False, description="Whether this is a deferred deep link")


class ResolveDeepLinkResponse(BaseModel):
    """Response with resolved deep link destination."""
    valid: bool = Field(..., description="Whether link is valid")
    destination: Optional[DeepLinkDestination] = Field(
        None,
        description="Resolved destination"
    )
    error: Optional[str] = Field(None, description="Error if link is invalid")
    attribution: Optional[Dict[str, Any]] = Field(
        None,
        description="Attribution data for analytics"
    )


class BatchDeepLinksRequest(BaseModel):
    """Request to generate multiple deep links."""
    links: List[DeepLinkParams] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of deep link parameters"
    )
    short_links: bool = Field(default=True, description="Generate short links")


class BatchDeepLinksResponse(BaseModel):
    """Response with batch of generated deep links."""
    links: List[CreateDeepLinkResponse] = Field(..., description="Generated links")
    success_count: int = Field(..., description="Number of successfully generated links")
    error_count: int = Field(..., description="Number of failed links")


class DeepLinkAnalyticsRequest(BaseModel):
    """Request to get deep link analytics."""
    link_id: Optional[str] = Field(None, description="Specific link ID")
    days: int = Field(default=7, ge=1, le=90, description="Days of analytics data")


class DeepLinkStats(BaseModel):
    """Statistics for a deep link."""
    link_url: str = Field(..., description="Link URL")
    clicks_total: int = Field(default=0, description="Total clicks")
    clicks_ios: int = Field(default=0, description="iOS clicks")
    clicks_android: int = Field(default=0, description="Android clicks")
    clicks_web: int = Field(default=0, description="Web fallback clicks")
    installs_total: int = Field(default=0, description="App installs attributed")
    first_opens: int = Field(default=0, description="First app opens")
    re_opens: int = Field(default=0, description="App re-opens")
    created_at: str = Field(..., description="Link creation timestamp")


class DeepLinkAnalyticsResponse(BaseModel):
    """Response with deep link analytics."""
    links: List[DeepLinkStats] = Field(default_factory=list, description="Link statistics")
    period_start: str = Field(..., description="Analytics period start")
    period_end: str = Field(..., description="Analytics period end")
    total_clicks: int = Field(default=0, description="Total clicks across all links")
    total_installs: int = Field(default=0, description="Total installs across all links")
