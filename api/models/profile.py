"""
User Profile Models

Pydantic models for user profile management, including:
- Full profile with workspace memberships
- Public profile with context card visibility
- Profile updates and preferences
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


# === Enums ===

class ProfileVisibility(str, Enum):
    """Profile visibility levels."""
    PUBLIC = "public"
    FRIENDS = "friends"
    WORK = "work"
    PRIVATE = "private"


class AccountStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"


# === Profile Data Models ===

class ProfileWorkspaceSummary(BaseModel):
    """Summary of a workspace the user belongs to."""
    id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Workspace name")
    role: str = Field(..., description="User's role in workspace")
    is_personal: bool = Field(default=False, description="Whether this is user's personal workspace")
    is_active: bool = Field(default=False, description="Whether this is the currently active workspace")
    member_count: int = Field(default=1, description="Number of members")


class ProfilePreferences(BaseModel):
    """User's profile preferences."""
    timezone: str = Field(default="America/Los_Angeles", description="User's timezone")
    language: str = Field(default="en", description="Preferred language code")
    theme: str = Field(default="system", description="UI theme preference (light/dark/system)")
    notifications_enabled: bool = Field(default=True, description="Global notification toggle")
    email_notifications: bool = Field(default=True, description="Email notification preference")
    daily_digest: bool = Field(default=False, description="Receive daily digest email")
    weekly_summary: bool = Field(default=False, description="Receive weekly summary")


class ProfileStats(BaseModel):
    """User activity statistics."""
    workspace_count: int = Field(default=0, description="Number of workspaces")
    documents_uploaded: int = Field(default=0, description="Total documents uploaded")
    total_sessions: int = Field(default=0, description="Total login sessions")
    last_active: Optional[str] = Field(None, description="Last activity timestamp")
    member_since: Optional[str] = Field(None, description="Account creation date")


class UserProfile(BaseModel):
    """Complete user profile as returned by /me endpoint."""
    id: str = Field(..., description="User's unique ID (Firebase UID)")
    email: Optional[str] = Field(None, description="User's email address")
    email_verified: bool = Field(default=False, description="Whether email is verified")
    name: Optional[str] = Field(None, description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")

    # Account info
    status: AccountStatus = Field(default=AccountStatus.ACTIVE, description="Account status")
    created_at: Optional[str] = Field(None, description="Account creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last profile update timestamp")

    # Context card integration
    headline: Optional[str] = Field(None, description="Professional headline from context card")
    bio: Optional[str] = Field(None, description="Bio from context card public tier")

    # Workspace memberships
    workspaces: List[ProfileWorkspaceSummary] = Field(default_factory=list, description="Workspace memberships")
    active_workspace_id: Optional[str] = Field(None, description="Currently active workspace ID")

    # Preferences
    preferences: ProfilePreferences = Field(default_factory=ProfilePreferences, description="User preferences")

    # Stats
    stats: ProfileStats = Field(default_factory=ProfileStats, description="User activity stats")

    # Raw data for extensibility
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PublicProfile(BaseModel):
    """Public-facing profile that respects context card visibility."""
    id: str = Field(..., description="User ID")
    name: Optional[str] = Field(None, description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    headline: Optional[str] = Field(None, description="Professional headline")
    bio: Optional[str] = Field(None, description="Public bio")

    # Visibility-controlled fields
    interests: List[str] = Field(default_factory=list, description="User's interests (if visible)")
    skills: List[str] = Field(default_factory=list, description="User's skills (if visible)")

    # Workspace context (only shown if in same workspace)
    workspace_role: Optional[str] = Field(None, description="Role in shared workspace (if any)")
    workspace_name: Optional[str] = Field(None, description="Shared workspace name (if any)")

    # Relationship
    relationship: Optional[str] = Field(None, description="Relationship to requesting user")


# === Request/Update Models ===

class ProfileUpdate(BaseModel):
    """Profile update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    headline: Optional[str] = Field(None, max_length=200, description="Professional headline")
    bio: Optional[str] = Field(None, max_length=1000, description="Bio")
    timezone: Optional[str] = Field(None, description="Timezone")
    language: Optional[str] = Field(None, min_length=2, max_length=10, description="Language code")
    theme: Optional[str] = Field(None, description="Theme preference")


class PreferencesUpdate(BaseModel):
    """Update user preferences."""
    timezone: Optional[str] = Field(None, description="Timezone")
    language: Optional[str] = Field(None, description="Language code")
    theme: Optional[str] = Field(None, description="Theme preference")
    notifications_enabled: Optional[bool] = Field(None, description="Global notifications")
    email_notifications: Optional[bool] = Field(None, description="Email notifications")
    daily_digest: Optional[bool] = Field(None, description="Daily digest")
    weekly_summary: Optional[bool] = Field(None, description="Weekly summary")


class AccountDeleteRequest(BaseModel):
    """Request to delete user account."""
    confirmation: str = Field(..., description="Must be 'DELETE' to confirm")
    feedback: Optional[str] = Field(None, description="Optional reason for leaving")
    export_data: bool = Field(default=True, description="Export user data before deletion")


class DataExportRequest(BaseModel):
    """Request to export user data."""
    include_documents: bool = Field(default=True, description="Include uploaded documents")
    include_history: bool = Field(default=True, description="Include activity history")
    include_preferences: bool = Field(default=True, description="Include preferences")
    format: str = Field(default="json", description="Export format (json/zip)")


# === Response Models ===

class ProfileResponse(BaseModel):
    """Response containing user profile."""
    profile: UserProfile
    edit_url: Optional[str] = Field(None, description="URL to edit profile")


class PublicProfileResponse(BaseModel):
    """Response containing public profile."""
    profile: PublicProfile
    visibility_level: ProfileVisibility = Field(..., description="What tier of visibility was used")
    is_connected: bool = Field(default=False, description="Whether users are connected")


class ProfileUpdateResponse(BaseModel):
    """Response after profile update."""
    profile: UserProfile
    updated_fields: List[str] = Field(default_factory=list, description="Fields that were updated")
    message: str = Field(default="Profile updated successfully", description="Status message")


class PreferencesResponse(BaseModel):
    """Response containing user preferences."""
    preferences: ProfilePreferences
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class AccountDeleteResponse(BaseModel):
    """Response after account deletion request."""
    status: str = Field(..., description="Deletion status")
    export_url: Optional[str] = Field(None, description="URL to download exported data")
    scheduled_deletion: Optional[str] = Field(None, description="Scheduled deletion timestamp")
    message: str = Field(..., description="Status message")


class DataExportResponse(BaseModel):
    """Response with data export information."""
    export_id: str = Field(..., description="Export job ID")
    status: str = Field(..., description="Export status (pending/processing/ready/failed)")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[str] = Field(None, description="When download link expires")
    size_bytes: Optional[int] = Field(None, description="Export file size")
