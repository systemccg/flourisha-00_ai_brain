"""
Pydantic Models for Content Intelligence
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VisibilityLevel(str, Enum):
    """Content visibility levels"""
    PRIVATE = "private"
    GROUP = "group"  # Format: "group:engineering"
    TENANT = "tenant"


class ContentType(str, Enum):
    """Types of content"""
    YOUTUBE_VIDEO = "youtube_video"
    VOICE_NOTE = "voice_note"
    MEETING_TRANSCRIPT = "meeting_transcript"
    LIMITLESS_NOTE = "limitless_note"
    DOCUMENT = "document"


class ProcessingStatus(str, Enum):
    """Processing queue statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request/Response Models

class ContentSummary(BaseModel):
    """AI-generated content summary"""
    summary: str = Field(..., description="2-3 paragraph summary")
    key_insights: List[str] = Field(default_factory=list, description="Key insights extracted")
    action_items: List[str] = Field(default_factory=list, description="Actionable items")
    tags: List[str] = Field(default_factory=list, description="Auto-generated tags")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance to project")


class ProcessedContentCreate(BaseModel):
    """Create new processed content"""
    title: str
    content_type: ContentType
    source_url: Optional[HttpUrl] = None
    source_id: Optional[str] = None  # e.g., YouTube video ID
    transcript: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None
    project_id: Optional[str] = None
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    shared_with: List[str] = Field(default_factory=list)  # ['group:X', 'user:Y']


class ProcessedContentResponse(BaseModel):
    """Processed content response"""
    id: str
    tenant_id: str
    tenant_user_id: str
    created_by_user_id: str
    title: str
    content_type: ContentType
    source_url: Optional[str] = None
    source_id: Optional[str] = None

    # AI-generated fields
    summary: Optional[str] = None
    key_insights: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    relevance_score: Optional[float] = None

    # Storage locations
    file_path: Optional[str] = None
    neo4j_node_id: Optional[str] = None
    vector_id: Optional[str] = None

    # Access control
    visibility: VisibilityLevel
    shared_with: List[str] = Field(default_factory=list)

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    """Create new project"""
    name: str
    description: Optional[str] = None
    tech_stack: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tech stack preferences for AI context awareness",
        example={
            "vector_db": "Supabase/PG Vector",
            "backend": "FastAPI",
            "frontend": "React",
            "mobile": "React Native"
        }
    )
    context_replacements: Dict[str, str] = Field(
        default_factory=dict,
        description="AI will translate these terms in content",
        example={"Qdrant": "Supabase/PG Vector", "Pinecone": "Supabase/PG Vector"}
    )
    default_visibility: VisibilityLevel = VisibilityLevel.PRIVATE


class ProjectResponse(BaseModel):
    """Project response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    tech_stack: Dict[str, Any]
    context_replacements: Dict[str, str]
    default_visibility: VisibilityLevel
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class YouTubePlaylistSubscription(BaseModel):
    """Subscribe to YouTube playlist"""
    playlist_id: str
    playlist_name: Optional[str] = None
    project_id: Optional[str] = None
    auto_process: bool = True


class YouTubeChannelSubscription(BaseModel):
    """Subscribe to YouTube channel"""
    channel_id: str
    channel_name: Optional[str] = None
    project_id: Optional[str] = None
    auto_process: bool = True


class ProcessingQueueItem(BaseModel):
    """Processing queue item"""
    id: str
    source_type: str  # 'youtube_playlist', 'youtube_channel', etc.
    source_id: str
    status: ProcessingStatus
    error_message: Optional[str] = None
    retry_count: int = 0
    scheduled_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
