"""
Context Card Models

Pydantic models for the Context Card API - a tiered visibility profile
system that controls what information different audiences see about a user.

Tiers:
- public: Anyone can see (name, headline, public portfolio)
- friends: Personal connections (interests, hobbies, personal AI preferences)
- work: Professional connections (skills, experience, work style)
- workspace:{ID}: Specific workspace only (role, work products, org-specific context)
- private: Only the user (personal notes, private AI learnings)
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ContextCardTier(str, Enum):
    """Context card visibility tiers."""
    PUBLIC = "public"
    FRIENDS = "friends"
    WORK = "work"
    WORKSPACE = "workspace"  # workspace:{id} for specific workspaces
    PRIVATE = "private"


class PublicTierContent(BaseModel):
    """Public tier - visible to anyone."""
    name: Optional[str] = Field(None, description="Display name")
    headline: Optional[str] = Field(None, description="Professional headline")
    bio: Optional[str] = Field(None, description="Short biography")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    portfolio_links: List[str] = Field(default_factory=list, description="Public portfolio links")
    location: Optional[str] = Field(None, description="General location (city, country)")


class FriendsTierContent(BaseModel):
    """Friends tier - visible to personal connections."""
    interests: List[str] = Field(default_factory=list, description="Personal interests")
    hobbies: List[str] = Field(default_factory=list, description="Hobbies and activities")
    values: List[str] = Field(default_factory=list, description="Core personal values")
    communication_style: Optional[str] = Field(None, description="How they prefer to communicate")
    ai_personality_preferences: Optional[Dict[str, Any]] = Field(
        None, description="AI interaction preferences"
    )
    fun_facts: List[str] = Field(default_factory=list, description="Fun facts about them")


class WorkTierContent(BaseModel):
    """Work tier - visible to professional connections."""
    skills: List[str] = Field(default_factory=list, description="Professional skills")
    experience_summary: Optional[str] = Field(None, description="Work experience summary")
    work_style: Optional[str] = Field(None, description="How they work (remote/office, hours)")
    strengths: List[str] = Field(default_factory=list, description="Key professional strengths")
    industries: List[str] = Field(default_factory=list, description="Industries worked in")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")


class WorkspaceTierContent(BaseModel):
    """Workspace-specific tier - visible only to specific workspace members."""
    workspace_id: str = Field(..., description="Workspace ID this tier belongs to")
    role: Optional[str] = Field(None, description="Role within the workspace")
    department: Optional[str] = Field(None, description="Department or team")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    projects: List[str] = Field(default_factory=list, description="Current projects")
    ai_context: Optional[Dict[str, Any]] = Field(
        None, description="Workspace-specific AI context"
    )


class PrivateTierContent(BaseModel):
    """Private tier - visible only to the user themselves."""
    personal_notes: Optional[str] = Field(None, description="Private notes")
    goals: List[str] = Field(default_factory=list, description="Personal goals")
    reflections: Optional[str] = Field(None, description="Personal reflections")
    ai_learnings: Optional[Dict[str, Any]] = Field(
        None, description="What AI has learned about user"
    )
    framework_insights: Optional[Dict[str, Any]] = Field(
        None, description="Personality framework mappings (MBTI, Enneagram, etc.)"
    )
    question_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Answered discovery questions"
    )


class ContextCard(BaseModel):
    """Complete context card with all tiers."""
    user_id: str = Field(..., description="User ID who owns this card")
    public: PublicTierContent = Field(default_factory=PublicTierContent)
    friends: FriendsTierContent = Field(default_factory=FriendsTierContent)
    work: WorkTierContent = Field(default_factory=WorkTierContent)
    workspaces: Dict[str, WorkspaceTierContent] = Field(
        default_factory=dict, description="Workspace-specific tiers keyed by workspace_id"
    )
    private: PrivateTierContent = Field(default_factory=PrivateTierContent)
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class ContextCardResponse(BaseModel):
    """Response containing a context card."""
    card: ContextCard = Field(..., description="The context card")
    editable_tiers: List[str] = Field(
        default_factory=list, description="Tiers user can edit"
    )


class TierUpdateRequest(BaseModel):
    """Request to update a specific tier."""
    content: Dict[str, Any] = Field(..., description="New tier content")


class TierUpdateResponse(BaseModel):
    """Response after updating a tier."""
    tier: str = Field(..., description="Updated tier name")
    updated_at: str = Field(..., description="Update timestamp")


class ConversationUpdateRequest(BaseModel):
    """Request to update context card from conversation analysis."""
    conversation_id: str = Field(..., description="Conversation ID to analyze")
    updates: Optional[Dict[str, Any]] = Field(
        None, description="Optional specific updates to apply"
    )


class ConversationUpdateResponse(BaseModel):
    """Response after updating from conversation."""
    fields_updated: List[str] = Field(..., description="Fields that were updated")
    tier_changes: Dict[str, int] = Field(
        default_factory=dict, description="Count of changes per tier"
    )


class ExportFormat(str, Enum):
    """Export format options."""
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"


class ExportRequest(BaseModel):
    """Request to export context card."""
    format: ExportFormat = Field(ExportFormat.PDF, description="Export format")
    include_tiers: List[str] = Field(
        default_factory=lambda: ["public", "work"],
        description="Tiers to include in export"
    )
    include_framework_insights: bool = Field(
        False, description="Include personality framework mappings"
    )


class ExportResponse(BaseModel):
    """Response with export data."""
    format: str = Field(..., description="Export format used")
    content: Optional[str] = Field(None, description="Base64 encoded content (for PDF)")
    data: Optional[Dict[str, Any]] = Field(None, description="JSON/Markdown data")
    filename: str = Field(..., description="Suggested filename")


class ContextCardPreview(BaseModel):
    """Preview of context card as seen by a specific viewer."""
    visible_tiers: List[str] = Field(..., description="Tiers visible to the viewer")
    merged_content: Dict[str, Any] = Field(
        ..., description="Merged content from all visible tiers"
    )
    viewer_relationship: str = Field(
        ..., description="Relationship type (public, friend, colleague, workspace)"
    )


class PreviewRequest(BaseModel):
    """Request to preview card as seen by another user."""
    viewer_id: Optional[str] = Field(
        None, description="User ID to preview as (optional)"
    )
    relationship: Optional[str] = Field(
        None, description="Assumed relationship (public, friend, work)"
    )
    workspace_id: Optional[str] = Field(
        None, description="Workspace context for preview"
    )
