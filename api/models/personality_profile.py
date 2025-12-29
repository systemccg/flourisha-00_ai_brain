"""
Personality Profile Models

Pydantic models for the Personality Profile API - extends Context Card concept
to contacts, capturing communication styles, relationship context, and interaction
history for personalized responses (especially email).

Storage: Neo4j knowledge graph (entity nodes with profile properties)
Reference: FRONTEND_FEATURE_REGISTRY.md Section 3.1
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class RelationshipType(str, Enum):
    """Types of relationships with contacts."""
    FAMILY = "family"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    CLIENT = "client"
    VENDOR = "vendor"
    MENTOR = "mentor"
    MENTEE = "mentee"
    ACQUAINTANCE = "acquaintance"
    OTHER = "other"


class CommunicationPreference(str, Enum):
    """Communication style preferences."""
    FORMAL = "formal"
    CASUAL = "casual"
    BRIEF = "brief"
    DETAILED = "detailed"
    EMOJI_FRIENDLY = "emoji_friendly"
    PROFESSIONAL = "professional"


class ContactChannel(str, Enum):
    """Preferred communication channels."""
    EMAIL = "email"
    PHONE = "phone"
    TEXT = "text"
    SLACK = "slack"
    LINKEDIN = "linkedin"
    IN_PERSON = "in_person"
    VIDEO_CALL = "video_call"


# === Profile Section Models ===

class ContactIdentity(BaseModel):
    """Identity information for a contact."""
    name: str = Field(..., description="Full name of the contact")
    nickname: Optional[str] = Field(None, description="Nickname or preferred name")
    title: Optional[str] = Field(None, description="Job title or role")
    company: Optional[str] = Field(None, description="Company or organization")
    email: Optional[str] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")


class CommunicationStyle(BaseModel):
    """Communication style analysis for a contact."""
    formality: CommunicationPreference = Field(
        CommunicationPreference.PROFESSIONAL,
        description="Formality level in communication"
    )
    brevity_preference: str = Field(
        "moderate",
        description="Preference for short vs detailed messages (brief/moderate/detailed)"
    )
    response_timing: Optional[str] = Field(
        None,
        description="Typical response time pattern (e.g., 'same day', 'within 24h', 'weekly')"
    )
    tone_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords that characterize their communication tone"
    )
    greeting_style: Optional[str] = Field(
        None,
        description="How they typically greet (e.g., 'Hi', 'Dear', first name only)"
    )
    sign_off_style: Optional[str] = Field(
        None,
        description="How they typically sign off (e.g., 'Best', 'Thanks', 'Cheers')"
    )
    emoji_usage: bool = Field(
        False,
        description="Whether they use emojis in communication"
    )


class TopicsOfInterest(BaseModel):
    """Topics and expertise areas for a contact."""
    expertise_areas: List[str] = Field(
        default_factory=list,
        description="Areas of expertise or specialization"
    )
    conversation_topics: List[str] = Field(
        default_factory=list,
        description="Topics they frequently discuss"
    )
    hobbies: List[str] = Field(
        default_factory=list,
        description="Known hobbies and personal interests"
    )
    current_projects: List[str] = Field(
        default_factory=list,
        description="Current projects or initiatives they're working on"
    )


class RelationshipContext(BaseModel):
    """Relationship history and context with a contact."""
    relationship_type: RelationshipType = Field(
        RelationshipType.ACQUAINTANCE,
        description="Type of relationship"
    )
    how_met: Optional[str] = Field(
        None,
        description="How you met this person"
    )
    shared_history: Optional[str] = Field(
        None,
        description="Brief shared history or context"
    )
    mutual_connections: List[str] = Field(
        default_factory=list,
        description="Mutual connections or contacts"
    )
    relationship_strength: int = Field(
        3,
        ge=1, le=5,
        description="Relationship strength (1=weak, 5=strong)"
    )
    notes: Optional[str] = Field(
        None,
        description="Private notes about the relationship"
    )


class InteractionPatterns(BaseModel):
    """Interaction patterns and preferences for a contact."""
    preferred_channels: List[ContactChannel] = Field(
        default_factory=lambda: [ContactChannel.EMAIL],
        description="Preferred communication channels"
    )
    best_contact_times: Optional[str] = Field(
        None,
        description="Best times to reach them (e.g., 'mornings', 'after 5pm')"
    )
    timezone: Optional[str] = Field(
        None,
        description="Their timezone (e.g., 'America/New_York')"
    )
    last_interaction: Optional[str] = Field(
        None,
        description="Date of last interaction (ISO format)"
    )
    interaction_frequency: Optional[str] = Field(
        None,
        description="How often you interact (e.g., 'weekly', 'monthly')"
    )
    follow_up_needed: bool = Field(
        False,
        description="Whether a follow-up is needed"
    )
    follow_up_date: Optional[str] = Field(
        None,
        description="When to follow up (ISO format)"
    )


# === Main Profile Model ===

class PersonalityProfile(BaseModel):
    """
    Complete personality profile for a contact.

    Extends the Context Card concept to contacts, capturing communication
    styles, relationship context, and interaction history.
    """
    id: Optional[str] = Field(None, description="Unique profile ID")
    user_id: str = Field(..., description="User who owns this profile")

    # Profile sections
    identity: ContactIdentity = Field(..., description="Contact identity information")
    communication_style: CommunicationStyle = Field(
        default_factory=CommunicationStyle,
        description="Communication style analysis"
    )
    topics: TopicsOfInterest = Field(
        default_factory=TopicsOfInterest,
        description="Topics of interest and expertise"
    )
    relationship: RelationshipContext = Field(
        default_factory=RelationshipContext,
        description="Relationship context"
    )
    interaction_patterns: InteractionPatterns = Field(
        default_factory=InteractionPatterns,
        description="Interaction patterns and preferences"
    )

    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        description="User-defined tags for categorization"
    )
    source: Optional[str] = Field(
        None,
        description="How this profile was created (manual, email_analysis, import)"
    )
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    # Graph integration
    graph_entity_id: Optional[str] = Field(
        None,
        description="Neo4j entity ID for graph queries"
    )


# === API Request/Response Models ===

class ProfileListResponse(BaseModel):
    """Response for listing profiles."""
    profiles: List[PersonalityProfile] = Field(..., description="List of profiles")
    total: int = Field(..., description="Total number of profiles")


class ProfileCreateRequest(BaseModel):
    """Request to create a new personality profile."""
    identity: ContactIdentity = Field(..., description="Contact identity (required)")
    communication_style: Optional[CommunicationStyle] = Field(
        None, description="Communication style"
    )
    topics: Optional[TopicsOfInterest] = Field(
        None, description="Topics of interest"
    )
    relationship: Optional[RelationshipContext] = Field(
        None, description="Relationship context"
    )
    interaction_patterns: Optional[InteractionPatterns] = Field(
        None, description="Interaction patterns"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization"
    )


class ProfileUpdateRequest(BaseModel):
    """Request to update a personality profile."""
    identity: Optional[ContactIdentity] = Field(None, description="Update identity")
    communication_style: Optional[CommunicationStyle] = Field(
        None, description="Update communication style"
    )
    topics: Optional[TopicsOfInterest] = Field(
        None, description="Update topics"
    )
    relationship: Optional[RelationshipContext] = Field(
        None, description="Update relationship context"
    )
    interaction_patterns: Optional[InteractionPatterns] = Field(
        None, description="Update interaction patterns"
    )
    tags: Optional[List[str]] = Field(None, description="Update tags")


class EmailAnalysisRequest(BaseModel):
    """Request to update profile from email analysis."""
    email_id: str = Field(..., description="Email ID to analyze")
    update_fields: List[str] = Field(
        default_factory=lambda: ["communication_style"],
        description="Fields to update from analysis"
    )


class EmailAnalysisResponse(BaseModel):
    """Response from email analysis."""
    profile_id: str = Field(..., description="Updated profile ID")
    fields_updated: List[str] = Field(..., description="Fields that were updated")
    suggestions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Suggested updates based on email analysis"
    )


class CommunicationSuggestionRequest(BaseModel):
    """Request for communication approach suggestion."""
    topic: str = Field(..., description="Topic of communication")
    channel: Optional[ContactChannel] = Field(
        None, description="Intended communication channel"
    )


class CommunicationSuggestionResponse(BaseModel):
    """Suggested communication approach for a contact."""
    profile_id: str = Field(..., description="Contact profile ID")
    contact_name: str = Field(..., description="Contact name")
    suggested_tone: str = Field(..., description="Suggested tone for communication")
    suggested_greeting: Optional[str] = Field(None, description="Suggested greeting")
    suggested_sign_off: Optional[str] = Field(None, description="Suggested sign-off")
    key_points: List[str] = Field(
        default_factory=list,
        description="Key points to consider"
    )
    best_time: Optional[str] = Field(
        None, description="Best time to send"
    )
    channel_recommendation: Optional[ContactChannel] = Field(
        None, description="Recommended channel"
    )


class ProfileSearchRequest(BaseModel):
    """Request to search profiles."""
    query: str = Field(..., description="Search query", min_length=1)
    relationship_types: Optional[List[RelationshipType]] = Field(
        None, description="Filter by relationship types"
    )
    tags: Optional[List[str]] = Field(
        None, description="Filter by tags"
    )
    limit: int = Field(20, ge=1, le=100, description="Maximum results")


class ProfileSearchResponse(BaseModel):
    """Response from profile search."""
    profiles: List[PersonalityProfile] = Field(..., description="Matching profiles")
    total: int = Field(..., description="Total matches")
    query: str = Field(..., description="Original query")
