"""
Hedra Avatar Integration Models

Pydantic models for Hedra Character API integration.
Supports avatar generation, realtime avatars, and asset management.

Hedra API Reference: https://www.hedra.com/docs/api-reference/
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class HedraGenerationStatus(str, Enum):
    """Status of a Hedra generation job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HedraAssetType(str, Enum):
    """Types of assets in Hedra."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    AVATAR = "avatar"


class HedraModelType(str, Enum):
    """Available Hedra generation models."""
    CHARACTER_2 = "character-2"
    CHARACTER_3 = "character-3"


class HedraVoiceGender(str, Enum):
    """Voice gender for TTS."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


# === Asset Management ===

class HedraAsset(BaseModel):
    """A Hedra asset (image, audio, or video)."""
    id: str = Field(..., description="Unique asset ID")
    type: HedraAssetType = Field(..., description="Type of asset")
    name: Optional[str] = Field(None, description="Display name")
    url: Optional[str] = Field(None, description="Download URL (temporary)")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL for images/videos")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    duration_seconds: Optional[float] = Field(None, description="Duration for audio/video")
    width: Optional[int] = Field(None, description="Width in pixels for images/videos")
    height: Optional[int] = Field(None, description="Height in pixels for images/videos")
    file_size_bytes: Optional[int] = Field(None, description="File size")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class HedraAssetListResponse(BaseModel):
    """Response for listing assets."""
    assets: List[HedraAsset] = Field(..., description="List of assets")
    total: int = Field(..., description="Total number of assets")
    page: int = Field(default=1, description="Current page")
    limit: int = Field(default=50, description="Items per page")


class UploadImageRequest(BaseModel):
    """Request to upload an image for avatar creation."""
    name: Optional[str] = Field(None, description="Optional name for the image")
    # Image will be uploaded as file in multipart form


class UploadAudioRequest(BaseModel):
    """Request to upload audio for lip-sync."""
    name: Optional[str] = Field(None, description="Optional name for the audio")
    # Audio will be uploaded as file in multipart form


# === Voice Management ===

class HedraVoice(BaseModel):
    """A Hedra TTS voice option."""
    id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Display name")
    gender: HedraVoiceGender = Field(..., description="Voice gender")
    language: str = Field(default="en", description="Language code")
    accent: Optional[str] = Field(None, description="Accent variant")
    preview_url: Optional[str] = Field(None, description="Preview audio URL")
    description: Optional[str] = Field(None, description="Voice description")


class HedraVoiceListResponse(BaseModel):
    """Response for listing available voices."""
    voices: List[HedraVoice] = Field(..., description="Available voices")
    total: int = Field(..., description="Total count")


# === Avatar/Character Generation ===

class GenerateAvatarRequest(BaseModel):
    """Request to generate an avatar video."""
    image_asset_id: str = Field(..., description="ID of the uploaded image asset")
    audio_asset_id: Optional[str] = Field(None, description="ID of uploaded audio for lip-sync")
    text: Optional[str] = Field(None, description="Text for TTS (if no audio_asset_id)")
    voice_id: Optional[str] = Field(None, description="Voice ID for TTS")
    model: HedraModelType = Field(default=HedraModelType.CHARACTER_2, description="Generation model")
    aspect_ratio: str = Field(default="1:1", description="Output aspect ratio (1:1, 16:9, 9:16)")
    # Advanced options
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for status updates")


class HedraGenerationJob(BaseModel):
    """A Hedra generation job."""
    id: str = Field(..., description="Job ID")
    status: HedraGenerationStatus = Field(..., description="Current status")
    model: HedraModelType = Field(..., description="Model used")
    image_asset_id: str = Field(..., description="Source image asset ID")
    audio_asset_id: Optional[str] = Field(None, description="Audio asset ID if used")
    output_asset_id: Optional[str] = Field(None, description="Output video asset ID (when complete)")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    progress_percent: Optional[int] = Field(None, description="Progress percentage (0-100)")
    credits_used: Optional[int] = Field(None, description="Credits consumed")


class GenerationJobListResponse(BaseModel):
    """Response for listing generation jobs."""
    jobs: List[HedraGenerationJob] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total count")
    page: int = Field(default=1, description="Current page")
    limit: int = Field(default=50, description="Items per page")


# === Realtime Avatar (LiveKit Integration) ===

class RealtimeAvatarSession(BaseModel):
    """A realtime avatar session."""
    session_id: str = Field(..., description="Session ID")
    avatar_id: str = Field(..., description="Avatar/image asset ID")
    status: str = Field(..., description="Session status (active, ended)")
    livekit_room: Optional[str] = Field(None, description="LiveKit room name")
    livekit_token: Optional[str] = Field(None, description="LiveKit token for client")
    created_at: datetime = Field(..., description="Session start time")
    ended_at: Optional[datetime] = Field(None, description="Session end time")


class CreateRealtimeSessionRequest(BaseModel):
    """Request to create a realtime avatar session."""
    avatar_id: str = Field(..., description="Avatar/image asset ID to use")
    session_name: Optional[str] = Field(None, description="Optional session name")
    max_duration_minutes: int = Field(default=30, description="Max session duration")
    webhook_url: Optional[str] = Field(None, description="Webhook for session events")


class RealtimeSessionResponse(BaseModel):
    """Response for realtime session creation."""
    session: RealtimeAvatarSession = Field(..., description="Session details")
    connection_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Connection details (WebSocket URL, tokens)"
    )


# === Credits / Billing ===

class HedraCreditsInfo(BaseModel):
    """Hedra account credits information."""
    balance: int = Field(..., description="Current credit balance")
    used_this_month: int = Field(default=0, description="Credits used this billing cycle")
    monthly_limit: Optional[int] = Field(None, description="Monthly limit if on subscription")
    plan_name: Optional[str] = Field(None, description="Current plan name")
    renewal_date: Optional[datetime] = Field(None, description="Next renewal date")


# === Project Management ===

class HedraProject(BaseModel):
    """A Hedra project container."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    generation_count: int = Field(default=0, description="Number of generations in project")
    is_shared: bool = Field(default=False, description="Whether project is shared")
    share_url: Optional[str] = Field(None, description="Public share URL if shared")


class HedraProjectListResponse(BaseModel):
    """Response for listing projects."""
    projects: List[HedraProject] = Field(..., description="List of projects")
    total: int = Field(..., description="Total count")


# === API Configuration ===

class HedraConfigStatus(BaseModel):
    """Status of Hedra API configuration."""
    is_configured: bool = Field(..., description="Whether API key is set")
    api_key_preview: Optional[str] = Field(None, description="First/last chars of API key")
    credits: Optional[HedraCreditsInfo] = Field(None, description="Current credits if connected")
    available_models: List[str] = Field(default_factory=list, description="Available generation models")
    last_verified: Optional[datetime] = Field(None, description="Last API verification time")


class UpdateHedraConfigRequest(BaseModel):
    """Request to update Hedra configuration."""
    api_key: str = Field(..., description="Hedra API key", min_length=10)
    # API key should be stored securely, not in plaintext


# === Webhook Events ===

class HedraWebhookEvent(BaseModel):
    """Incoming webhook event from Hedra."""
    event_type: str = Field(..., description="Event type (generation.completed, etc.)")
    job_id: Optional[str] = Field(None, description="Related job ID")
    session_id: Optional[str] = Field(None, description="Related session ID")
    status: Optional[str] = Field(None, description="Status update")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    timestamp: datetime = Field(..., description="Event timestamp")
