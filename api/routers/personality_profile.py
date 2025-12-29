"""
Personality Profile Router

API endpoints for managing contact personality profiles - extending the
Context Card concept to contacts for personalized communication.

Endpoints:
- GET  /api/profiles                    - List all profiles
- POST /api/profiles                    - Create new profile
- GET  /api/profiles/{id}               - Get profile by ID
- PUT  /api/profiles/{id}               - Update profile
- DELETE /api/profiles/{id}             - Delete profile
- POST /api/profiles/search             - Search profiles
- POST /api/profiles/{id}/analyze-email - Update from email analysis
- GET  /api/profiles/{id}/suggest       - Get communication suggestions

Storage: Currently in-memory (TODO: Neo4j graph storage)
Reference: FRONTEND_FEATURE_REGISTRY.md Section 3.1
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.personality_profile import (
    PersonalityProfile,
    ProfileListResponse,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    EmailAnalysisRequest,
    EmailAnalysisResponse,
    CommunicationSuggestionRequest,
    CommunicationSuggestionResponse,
    ProfileSearchRequest,
    ProfileSearchResponse,
    ContactIdentity,
    CommunicationStyle,
    TopicsOfInterest,
    RelationshipContext,
    InteractionPatterns,
    RelationshipType,
    CommunicationPreference,
    ContactChannel,
)
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/profiles", tags=["Personality Profiles"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_pacific_timestamp() -> str:
    """Get current timestamp in Pacific time."""
    return datetime.now(PACIFIC).isoformat()


# In-memory storage (TODO: Replace with Neo4j graph storage)
# Key: profile_id, Value: PersonalityProfile
_profiles_store: Dict[str, PersonalityProfile] = {}


def generate_profile_id() -> str:
    """Generate a unique profile ID."""
    return f"profile_{uuid.uuid4().hex[:12]}"


def get_user_profiles(user_id: str) -> List[PersonalityProfile]:
    """Get all profiles for a user."""
    return [p for p in _profiles_store.values() if p.user_id == user_id]


def get_profile_by_id(profile_id: str, user_id: str) -> Optional[PersonalityProfile]:
    """Get a specific profile if it belongs to the user."""
    profile = _profiles_store.get(profile_id)
    if profile and profile.user_id == user_id:
        return profile
    return None


# === CRUD Endpoints ===

@router.get(
    "",
    response_model=APIResponse[ProfileListResponse],
    summary="List all personality profiles",
    description="Returns all contact personality profiles for the authenticated user."
)
async def list_profiles(
    request: Request,
    relationship_type: Optional[RelationshipType] = Query(
        None, description="Filter by relationship type"
    ),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(50, ge=1, le=200, description="Maximum profiles to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse[ProfileListResponse]:
    """
    List all personality profiles for the current user.

    - Optional filtering by relationship type or tag
    - Supports pagination with limit/offset
    - Sorted by name alphabetically
    """
    profiles = get_user_profiles(user.uid)

    # Apply filters
    if relationship_type:
        profiles = [p for p in profiles if p.relationship.relationship_type == relationship_type]
    if tag:
        profiles = [p for p in profiles if tag in p.tags]

    # Sort by name
    profiles.sort(key=lambda p: p.identity.name.lower())

    # Pagination
    total = len(profiles)
    profiles = profiles[offset:offset + limit]

    response_data = ProfileListResponse(
        profiles=profiles,
        total=total
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.post(
    "",
    response_model=APIResponse[PersonalityProfile],
    summary="Create a new personality profile",
    description="Create a new contact personality profile."
)
async def create_profile(
    request: Request,
    body: ProfileCreateRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[PersonalityProfile]:
    """
    Create a new personality profile for a contact.

    - Identity information (name, email, etc.) is required
    - Other sections (communication style, topics, etc.) are optional
    - Profile is stored and can be updated later
    """
    now = get_pacific_timestamp()
    profile_id = generate_profile_id()

    profile = PersonalityProfile(
        id=profile_id,
        user_id=user.uid,
        identity=body.identity,
        communication_style=body.communication_style or CommunicationStyle(),
        topics=body.topics or TopicsOfInterest(),
        relationship=body.relationship or RelationshipContext(),
        interaction_patterns=body.interaction_patterns or InteractionPatterns(),
        tags=body.tags,
        source="manual",
        created_at=now,
        updated_at=now,
    )

    # Store profile
    _profiles_store[profile_id] = profile

    return APIResponse(
        success=True,
        data=profile,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.get(
    "/{profile_id}",
    response_model=APIResponse[PersonalityProfile],
    summary="Get a personality profile",
    description="Get a specific personality profile by ID."
)
async def get_profile(
    request: Request,
    profile_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[PersonalityProfile]:
    """
    Get a specific personality profile by ID.

    - Returns full profile with all sections
    - Only returns profiles owned by the authenticated user
    """
    profile = get_profile_by_id(profile_id, user.uid)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{profile_id}' not found"
        )

    return APIResponse(
        success=True,
        data=profile,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.put(
    "/{profile_id}",
    response_model=APIResponse[PersonalityProfile],
    summary="Update a personality profile",
    description="Update an existing personality profile."
)
async def update_profile(
    request: Request,
    profile_id: str,
    body: ProfileUpdateRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[PersonalityProfile]:
    """
    Update an existing personality profile.

    - Only updates provided fields
    - Non-provided fields retain their current values
    - Updates the updated_at timestamp
    """
    profile = get_profile_by_id(profile_id, user.uid)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{profile_id}' not found"
        )

    # Update only provided fields
    if body.identity is not None:
        profile.identity = body.identity
    if body.communication_style is not None:
        profile.communication_style = body.communication_style
    if body.topics is not None:
        profile.topics = body.topics
    if body.relationship is not None:
        profile.relationship = body.relationship
    if body.interaction_patterns is not None:
        profile.interaction_patterns = body.interaction_patterns
    if body.tags is not None:
        profile.tags = body.tags

    profile.updated_at = get_pacific_timestamp()

    # Update store
    _profiles_store[profile_id] = profile

    return APIResponse(
        success=True,
        data=profile,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.delete(
    "/{profile_id}",
    response_model=APIResponse[dict],
    summary="Delete a personality profile",
    description="Delete a personality profile by ID."
)
async def delete_profile(
    request: Request,
    profile_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[dict]:
    """
    Delete a personality profile.

    - Permanently removes the profile
    - Cannot be undone
    """
    profile = get_profile_by_id(profile_id, user.uid)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{profile_id}' not found"
        )

    # Remove from store
    del _profiles_store[profile_id]

    return APIResponse(
        success=True,
        data={
            "deleted": True,
            "profile_id": profile_id,
            "deleted_at": get_pacific_timestamp()
        },
        meta=ResponseMeta(**request.state.get_meta())
    )


# === Search Endpoint ===

@router.post(
    "/search",
    response_model=APIResponse[ProfileSearchResponse],
    summary="Search personality profiles",
    description="Search profiles by name, company, tags, or relationship type."
)
async def search_profiles(
    request: Request,
    body: ProfileSearchRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[ProfileSearchResponse]:
    """
    Search personality profiles.

    - Searches name, company, email, and tags
    - Optional filtering by relationship type
    - Results sorted by relevance
    """
    profiles = get_user_profiles(user.uid)
    query_lower = body.query.lower()

    # Score and filter profiles
    scored_profiles = []
    for profile in profiles:
        score = 0

        # Name match (highest priority)
        if query_lower in profile.identity.name.lower():
            score += 100

        # Company match
        if profile.identity.company and query_lower in profile.identity.company.lower():
            score += 50

        # Email match
        if profile.identity.email and query_lower in profile.identity.email.lower():
            score += 40

        # Tag match
        for tag in profile.tags:
            if query_lower in tag.lower():
                score += 30

        # Topics match
        for topic in profile.topics.expertise_areas + profile.topics.conversation_topics:
            if query_lower in topic.lower():
                score += 20

        if score > 0:
            scored_profiles.append((score, profile))

    # Apply relationship type filter
    if body.relationship_types:
        scored_profiles = [
            (s, p) for s, p in scored_profiles
            if p.relationship.relationship_type in body.relationship_types
        ]

    # Apply tag filter
    if body.tags:
        scored_profiles = [
            (s, p) for s, p in scored_profiles
            if any(t in p.tags for t in body.tags)
        ]

    # Sort by score descending
    scored_profiles.sort(key=lambda x: -x[0])

    # Apply limit
    total = len(scored_profiles)
    results = [p for _, p in scored_profiles[:body.limit]]

    return APIResponse(
        success=True,
        data=ProfileSearchResponse(
            profiles=results,
            total=total,
            query=body.query
        ),
        meta=ResponseMeta(**request.state.get_meta())
    )


# === Email Analysis Endpoint ===

@router.post(
    "/{profile_id}/analyze-email",
    response_model=APIResponse[EmailAnalysisResponse],
    summary="Update profile from email analysis",
    description="Analyze an email to update communication style and patterns."
)
async def analyze_email(
    request: Request,
    profile_id: str,
    body: EmailAnalysisRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[EmailAnalysisResponse]:
    """
    Update profile based on email analysis.

    - Analyzes email content to extract communication patterns
    - Updates specified fields (communication_style by default)
    - Returns suggestions for manual review

    TODO: Integrate with Gmail service and LLM for actual analysis
    """
    profile = get_profile_by_id(profile_id, user.uid)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{profile_id}' not found"
        )

    # TODO: Actual email analysis implementation
    # For now, return a placeholder response

    # Placeholder: Simulate some suggestions
    suggestions = {
        "communication_style": {
            "formality": "professional",
            "brevity_preference": "moderate",
            "emoji_usage": False,
            "greeting_style": "Hi {first_name}",
            "sign_off_style": "Best regards"
        },
        "response_timing": "typically responds within 24 hours"
    }

    return APIResponse(
        success=True,
        data=EmailAnalysisResponse(
            profile_id=profile_id,
            fields_updated=[],  # No actual updates in placeholder
            suggestions=suggestions
        ),
        meta=ResponseMeta(**request.state.get_meta())
    )


# === Communication Suggestion Endpoint ===

@router.get(
    "/{profile_id}/suggest",
    response_model=APIResponse[CommunicationSuggestionResponse],
    summary="Get communication suggestions",
    description="Get personalized communication approach for a contact."
)
async def suggest_communication(
    request: Request,
    profile_id: str,
    topic: str = Query(..., description="Topic of communication"),
    channel: Optional[ContactChannel] = Query(
        None, description="Intended communication channel"
    ),
    user: UserContext = Depends(get_current_user)
) -> APIResponse[CommunicationSuggestionResponse]:
    """
    Get suggestions for how to communicate with a contact.

    - Based on their communication style preferences
    - Considers the topic and intended channel
    - Returns tone, greeting, sign-off suggestions
    """
    profile = get_profile_by_id(profile_id, user.uid)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{profile_id}' not found"
        )

    # Build suggestions based on profile
    comm_style = profile.communication_style
    interaction = profile.interaction_patterns

    # Determine suggested tone
    tone_map = {
        CommunicationPreference.FORMAL: "formal and professional",
        CommunicationPreference.CASUAL: "casual and friendly",
        CommunicationPreference.BRIEF: "concise and to-the-point",
        CommunicationPreference.DETAILED: "thorough and detailed",
        CommunicationPreference.PROFESSIONAL: "professional but approachable",
        CommunicationPreference.EMOJI_FRIENDLY: "warm and friendly, emojis welcome"
    }
    suggested_tone = tone_map.get(comm_style.formality, "professional")

    # Build key points
    key_points = []
    if comm_style.brevity_preference == "brief":
        key_points.append("Keep message concise - they prefer brevity")
    elif comm_style.brevity_preference == "detailed":
        key_points.append("Include context and details - they appreciate thoroughness")

    if comm_style.emoji_usage:
        key_points.append("Emojis are acceptable in this conversation")

    if profile.relationship.relationship_type == RelationshipType.CLIENT:
        key_points.append("This is a client - maintain professionalism")
    elif profile.relationship.relationship_type == RelationshipType.FRIEND:
        key_points.append("This is a friend - casual tone is fine")

    # Get channel recommendation
    recommended_channel = channel
    if not recommended_channel and interaction.preferred_channels:
        recommended_channel = interaction.preferred_channels[0]

    return APIResponse(
        success=True,
        data=CommunicationSuggestionResponse(
            profile_id=profile_id,
            contact_name=profile.identity.name,
            suggested_tone=suggested_tone,
            suggested_greeting=comm_style.greeting_style,
            suggested_sign_off=comm_style.sign_off_style,
            key_points=key_points,
            best_time=interaction.best_contact_times,
            channel_recommendation=recommended_channel
        ),
        meta=ResponseMeta(**request.state.get_meta())
    )


# === Stats Endpoint ===

@router.get(
    "/stats",
    response_model=APIResponse[dict],
    summary="Get profile statistics",
    description="Get statistics about your personality profiles."
)
async def get_profile_stats(
    request: Request,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[dict]:
    """
    Get statistics about your personality profiles.

    - Total profile count
    - Count by relationship type
    - Count by tag
    """
    profiles = get_user_profiles(user.uid)

    # Count by relationship type
    by_relationship = {}
    for profile in profiles:
        rel_type = profile.relationship.relationship_type.value
        by_relationship[rel_type] = by_relationship.get(rel_type, 0) + 1

    # Count by tag
    by_tag = {}
    for profile in profiles:
        for tag in profile.tags:
            by_tag[tag] = by_tag.get(tag, 0) + 1

    # Get all unique tags
    all_tags = sorted(by_tag.keys())

    # Count with follow-up needed
    follow_up_needed = len([
        p for p in profiles
        if p.interaction_patterns.follow_up_needed
    ])

    return APIResponse(
        success=True,
        data={
            "total_profiles": len(profiles),
            "by_relationship_type": by_relationship,
            "by_tag": by_tag,
            "all_tags": all_tags,
            "follow_ups_needed": follow_up_needed
        },
        meta=ResponseMeta(**request.state.get_meta())
    )
