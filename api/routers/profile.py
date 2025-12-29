"""
User Profile Router

API endpoints for user profile management:
- GET  /api/profile/me         - Get current user's full profile with workspaces
- PATCH /api/profile/me        - Update profile fields
- GET  /api/profile/preferences - Get user preferences
- PATCH /api/profile/preferences - Update preferences
- GET  /api/profile/user/{id}  - Get another user's public profile (visibility-controlled)
- POST /api/profile/export     - Request data export
- DELETE /api/profile/me       - Delete account (cascade)

Acceptance Criteria:
- /me returns full profile with workspaces
- Public profile respects context card visibility
- Delete cascades properly
"""
import os
import logging
import uuid
from datetime import datetime
from typing import Optional, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel

from models.response import APIResponse, ResponseMeta
from models.profile import (
    UserProfile,
    PublicProfile,
    ProfileWorkspaceSummary,
    ProfilePreferences,
    ProfileStats,
    ProfileUpdate,
    PreferencesUpdate,
    AccountDeleteRequest,
    DataExportRequest,
    ProfileResponse,
    PublicProfileResponse,
    ProfileUpdateResponse,
    PreferencesResponse,
    AccountDeleteResponse,
    DataExportResponse,
    ProfileVisibility,
    AccountStatus,
)
from middleware.auth import get_current_user, get_optional_user, UserContext
from config import get_settings


router = APIRouter(prefix="/api/profile", tags=["Profile"])

logger = logging.getLogger("flourisha.api.profile")
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Supabase Client ===

def get_supabase():
    """Get Supabase client for profile operations."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured"
        )

    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_service_key)


# === Helper Functions ===

def now_pacific() -> str:
    """Get current time in Pacific timezone as ISO string."""
    return datetime.now(PACIFIC).isoformat()


async def get_user_data(user_id: str, supabase) -> Optional[dict]:
    """Get user data from users table."""
    try:
        result = supabase.table("users").select("*").eq("id", user_id).single().execute()
        return result.data
    except Exception as e:
        logger.warning(f"User {user_id} not found: {e}")
        return None


async def get_user_preferences(user_id: str, supabase) -> dict:
    """Get user preferences from user_preferences table."""
    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
        return result.data or {}
    except Exception:
        return {}


async def get_user_workspaces(user_id: str, supabase) -> List[ProfileWorkspaceSummary]:
    """Get user's workspace memberships."""
    try:
        result = supabase.table("tenant_users").select(
            "tenant_id, role, created_at, tenants(tenant_id, name, settings)"
        ).eq("user_id", user_id).execute()

        # Get active workspace
        pref_result = supabase.table("user_preferences").select(
            "active_workspace_id"
        ).eq("user_id", user_id).single().execute()
        active_ws_id = pref_result.data.get("active_workspace_id") if pref_result.data else None

        workspaces = []
        for membership in result.data or []:
            tenant = membership.get("tenants", {}) or {}
            ws_id = membership.get("tenant_id") or tenant.get("tenant_id")
            if not ws_id:
                continue

            settings = tenant.get("settings", {}) or {}

            # Get member count
            count_result = supabase.table("tenant_users").select(
                "user_id", count="exact"
            ).eq("tenant_id", ws_id).execute()

            workspaces.append(ProfileWorkspaceSummary(
                id=ws_id,
                name=tenant.get("name", "Unknown"),
                role=membership.get("role", "member"),
                is_personal=settings.get("is_personal", False),
                is_active=(ws_id == active_ws_id),
                member_count=count_result.count or 1,
            ))

        return workspaces
    except Exception as e:
        logger.error(f"Error fetching workspaces for user {user_id}: {e}")
        return []


async def get_context_card_public(user_id: str, supabase) -> dict:
    """Get public tier from user's context card."""
    try:
        # TODO: Replace with actual context card table when implemented
        # For now, return from users table metadata or empty
        user_data = await get_user_data(user_id, supabase)
        if user_data:
            return {
                "headline": user_data.get("headline"),
                "bio": user_data.get("bio"),
            }
        return {}
    except Exception:
        return {}


async def get_user_stats(user_id: str, supabase) -> ProfileStats:
    """Get user activity statistics."""
    try:
        # Get workspace count
        ws_result = supabase.table("tenant_users").select(
            "tenant_id", count="exact"
        ).eq("user_id", user_id).execute()

        # Get document count (if documents table exists)
        doc_count = 0
        try:
            doc_result = supabase.table("documents").select(
                "id", count="exact"
            ).eq("uploaded_by", user_id).execute()
            doc_count = doc_result.count or 0
        except Exception:
            pass

        # Get user creation date
        user_data = await get_user_data(user_id, supabase)
        created_at = user_data.get("created_at") if user_data else None

        return ProfileStats(
            workspace_count=ws_result.count or 0,
            documents_uploaded=doc_count,
            total_sessions=0,  # Would need session tracking
            last_active=now_pacific(),
            member_since=created_at,
        )
    except Exception as e:
        logger.error(f"Error fetching stats for user {user_id}: {e}")
        return ProfileStats()


def prefs_dict_to_model(prefs: dict) -> ProfilePreferences:
    """Convert preferences dict to ProfilePreferences model."""
    return ProfilePreferences(
        timezone=prefs.get("timezone", "America/Los_Angeles"),
        language=prefs.get("language", "en"),
        theme=prefs.get("theme", "system"),
        notifications_enabled=prefs.get("notifications_enabled", True),
        email_notifications=prefs.get("email_notifications", True),
        daily_digest=prefs.get("daily_digest", False),
        weekly_summary=prefs.get("weekly_summary", False),
    )


async def build_user_profile(user: UserContext, supabase) -> UserProfile:
    """Build complete user profile from all data sources."""
    # Get user data
    user_data = await get_user_data(user.uid, supabase) or {}

    # Get preferences
    prefs_data = await get_user_preferences(user.uid, supabase)
    preferences = prefs_dict_to_model(prefs_data)

    # Get workspaces
    workspaces = await get_user_workspaces(user.uid, supabase)

    # Get context card public tier
    context_public = await get_context_card_public(user.uid, supabase)

    # Get stats
    stats = await get_user_stats(user.uid, supabase)

    # Find active workspace
    active_ws_id = None
    for ws in workspaces:
        if ws.is_active:
            active_ws_id = ws.id
            break

    return UserProfile(
        id=user.uid,
        email=user.email or user_data.get("email"),
        email_verified=user.email_verified,
        name=user.name or user_data.get("display_name"),
        avatar_url=user.picture or user_data.get("avatar_url"),
        status=AccountStatus.ACTIVE,
        created_at=user_data.get("created_at"),
        updated_at=user_data.get("updated_at"),
        headline=context_public.get("headline"),
        bio=context_public.get("bio"),
        workspaces=workspaces,
        active_workspace_id=active_ws_id,
        preferences=preferences,
        stats=stats,
        metadata=user_data.get("metadata", {}),
    )


async def determine_visibility(viewer_id: str, target_id: str, supabase) -> ProfileVisibility:
    """Determine what visibility tier the viewer has for the target user."""
    # Same user = private access
    if viewer_id == target_id:
        return ProfileVisibility.PRIVATE

    # Check if in same workspace
    try:
        viewer_ws = supabase.table("tenant_users").select("tenant_id").eq("user_id", viewer_id).execute()
        target_ws = supabase.table("tenant_users").select("tenant_id").eq("user_id", target_id).execute()

        viewer_tenant_ids = {m.get("tenant_id") for m in viewer_ws.data or []}
        target_tenant_ids = {m.get("tenant_id") for m in target_ws.data or []}

        if viewer_tenant_ids & target_tenant_ids:
            return ProfileVisibility.WORK

    except Exception as e:
        logger.warning(f"Error checking workspace membership: {e}")

    # TODO: Check friends relationship when implemented
    # For now, default to public
    return ProfileVisibility.PUBLIC


async def get_shared_workspace(viewer_id: str, target_id: str, supabase) -> Optional[dict]:
    """Get the first shared workspace between two users."""
    try:
        viewer_ws = supabase.table("tenant_users").select(
            "tenant_id, role, tenants(name)"
        ).eq("user_id", viewer_id).execute()

        target_ws = supabase.table("tenant_users").select(
            "tenant_id, role"
        ).eq("user_id", target_id).execute()

        viewer_map = {m.get("tenant_id"): m for m in viewer_ws.data or []}
        for membership in target_ws.data or []:
            tid = membership.get("tenant_id")
            if tid in viewer_map:
                viewer_data = viewer_map[tid]
                return {
                    "workspace_id": tid,
                    "workspace_name": viewer_data.get("tenants", {}).get("name"),
                    "target_role": membership.get("role"),
                }
        return None
    except Exception:
        return None


# === Endpoints ===

@router.get("/me", response_model=APIResponse[ProfileResponse])
async def get_my_profile(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ProfileResponse]:
    """
    Get the current user's complete profile.

    Returns full profile including:
    - Basic info (name, email, avatar)
    - All workspace memberships with roles
    - User preferences
    - Activity statistics
    - Context card headline/bio

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        profile = await build_user_profile(user, supabase)

        return APIResponse(
            success=True,
            data=ProfileResponse(
                profile=profile,
                edit_url="/api/profile/me",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error fetching profile for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.patch("/me", response_model=APIResponse[ProfileUpdateResponse])
async def update_my_profile(
    updates: ProfileUpdate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ProfileUpdateResponse]:
    """
    Update current user's profile.

    Updateable fields:
    - name: Display name
    - avatar_url: Profile picture URL
    - headline: Professional headline
    - bio: Bio text
    - timezone, language, theme: Preferences

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Prepare updates for users table
        user_updates = {"updated_at": now_pacific()}
        updated_fields = []

        if updates.name is not None:
            user_updates["display_name"] = updates.name
            updated_fields.append("name")

        if updates.avatar_url is not None:
            user_updates["avatar_url"] = updates.avatar_url
            updated_fields.append("avatar_url")

        if updates.headline is not None:
            user_updates["headline"] = updates.headline
            updated_fields.append("headline")

        if updates.bio is not None:
            user_updates["bio"] = updates.bio
            updated_fields.append("bio")

        # Update users table if there are changes
        if len(user_updates) > 1:  # More than just updated_at
            supabase.table("users").upsert({
                "id": user.uid,
                **user_updates,
            }, on_conflict="id").execute()

        # Handle preferences updates
        prefs_updates = {}
        if updates.timezone is not None:
            prefs_updates["timezone"] = updates.timezone
            updated_fields.append("timezone")
        if updates.language is not None:
            prefs_updates["language"] = updates.language
            updated_fields.append("language")
        if updates.theme is not None:
            prefs_updates["theme"] = updates.theme
            updated_fields.append("theme")

        if prefs_updates:
            prefs_updates["user_id"] = user.uid
            prefs_updates["updated_at"] = now_pacific()
            supabase.table("user_preferences").upsert(
                prefs_updates, on_conflict="user_id"
            ).execute()

        # Fetch updated profile
        profile = await build_user_profile(user, supabase)

        logger.info(f"Updated profile for user {user.uid}: {updated_fields}")

        return APIResponse(
            success=True,
            data=ProfileUpdateResponse(
                profile=profile,
                updated_fields=updated_fields,
                message=f"Updated {len(updated_fields)} field(s)",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error updating profile for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/preferences", response_model=APIResponse[PreferencesResponse])
async def get_my_preferences(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[PreferencesResponse]:
    """
    Get current user's preferences.

    Returns notification settings, timezone, theme, etc.

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        prefs_data = await get_user_preferences(user.uid, supabase)
        preferences = prefs_dict_to_model(prefs_data)

        return APIResponse(
            success=True,
            data=PreferencesResponse(
                preferences=preferences,
                updated_at=prefs_data.get("updated_at"),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error fetching preferences for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.patch("/preferences", response_model=APIResponse[PreferencesResponse])
async def update_my_preferences(
    updates: PreferencesUpdate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[PreferencesResponse]:
    """
    Update current user's preferences.

    Updateable:
    - timezone, language, theme
    - notifications_enabled, email_notifications
    - daily_digest, weekly_summary

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Build update dict from non-None values
        update_data = {"user_id": user.uid, "updated_at": now_pacific()}

        updates_dict = updates.model_dump(exclude_none=True)
        update_data.update(updates_dict)

        # Upsert preferences
        supabase.table("user_preferences").upsert(
            update_data, on_conflict="user_id"
        ).execute()

        # Fetch updated preferences
        prefs_data = await get_user_preferences(user.uid, supabase)
        preferences = prefs_dict_to_model(prefs_data)

        logger.info(f"Updated preferences for user {user.uid}")

        return APIResponse(
            success=True,
            data=PreferencesResponse(
                preferences=preferences,
                updated_at=now_pacific(),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error updating preferences for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/user/{user_id}", response_model=APIResponse[PublicProfileResponse])
async def get_user_profile(
    user_id: str,
    request: Request,
    user: Optional[UserContext] = Depends(get_optional_user),
) -> APIResponse[PublicProfileResponse]:
    """
    Get another user's profile.

    Visibility depends on relationship:
    - Same workspace: See work tier (skills, work style)
    - Friends: See friends tier (interests, values)
    - Public: Only public tier (name, headline, bio)

    Works for authenticated and unauthenticated requests.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Get target user's data
        target_data = await get_user_data(user_id, supabase)
        if not target_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )

        # Determine visibility level
        viewer_id = user.uid if user else None
        visibility = ProfileVisibility.PUBLIC

        if viewer_id:
            visibility = await determine_visibility(viewer_id, user_id, supabase)

        # Get context card data based on visibility
        context_public = await get_context_card_public(user_id, supabase)

        # Build public profile
        profile = PublicProfile(
            id=user_id,
            name=target_data.get("display_name"),
            avatar_url=target_data.get("avatar_url"),
            headline=context_public.get("headline"),
            bio=context_public.get("bio"),
        )

        # Add visibility-tier specific data
        if visibility in (ProfileVisibility.WORK, ProfileVisibility.PRIVATE):
            # TODO: Get skills from context card work tier
            profile.skills = []

        if visibility in (ProfileVisibility.FRIENDS, ProfileVisibility.PRIVATE):
            # TODO: Get interests from context card friends tier
            profile.interests = []

        # Add shared workspace info if applicable
        if viewer_id and visibility == ProfileVisibility.WORK:
            shared = await get_shared_workspace(viewer_id, user_id, supabase)
            if shared:
                profile.workspace_role = shared.get("target_role")
                profile.workspace_name = shared.get("workspace_name")
                profile.relationship = "colleague"

        is_connected = visibility != ProfileVisibility.PUBLIC

        return APIResponse(
            success=True,
            data=PublicProfileResponse(
                profile=profile,
                visibility_level=visibility,
                is_connected=is_connected,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile for user {user_id}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/export", response_model=APIResponse[DataExportResponse])
async def request_data_export(
    export_request: DataExportRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DataExportResponse]:
    """
    Request an export of user's data.

    Creates an async job to export:
    - Profile data
    - Uploaded documents (optional)
    - Activity history (optional)
    - Preferences

    Export is available for download when ready.

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        export_id = f"export_{uuid.uuid4().hex[:12]}"

        # Create export job record
        export_job = {
            "id": export_id,
            "user_id": user.uid,
            "status": "pending",
            "include_documents": export_request.include_documents,
            "include_history": export_request.include_history,
            "include_preferences": export_request.include_preferences,
            "format": export_request.format,
            "created_at": now_pacific(),
        }

        # TODO: Store in export_jobs table and trigger async processing
        # For now, return pending status
        logger.info(f"Created export job {export_id} for user {user.uid}")

        return APIResponse(
            success=True,
            data=DataExportResponse(
                export_id=export_id,
                status="pending",
                download_url=None,  # Will be populated when ready
                expires_at=None,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error creating export for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/me", response_model=APIResponse[AccountDeleteResponse])
async def delete_my_account(
    delete_request: AccountDeleteRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AccountDeleteResponse]:
    """
    Delete current user's account.

    Requires confirmation string "DELETE".
    Optionally exports data before deletion.

    CASCADE BEHAVIOR:
    - Removes from all workspace memberships
    - Transfers ownership of owned workspaces (or deletes if personal)
    - Deletes personal workspace and all its data
    - Removes user preferences
    - Anonymizes activity history

    Deletion is scheduled (30 day grace period).

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify confirmation
        if delete_request.confirmation != "DELETE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation must be 'DELETE'"
            )

        # Optional: Export data first
        export_url = None
        if delete_request.export_data:
            # TODO: Trigger data export
            export_url = f"/api/profile/export/{uuid.uuid4().hex[:12]}"

        # Schedule deletion (30 day grace period)
        deletion_date = datetime.now(PACIFIC)
        # Add 30 days
        from datetime import timedelta
        scheduled_deletion = (deletion_date + timedelta(days=30)).isoformat()

        # Mark account for deletion
        supabase.table("users").update({
            "status": "pending_deletion",
            "scheduled_deletion": scheduled_deletion,
            "deletion_feedback": delete_request.feedback,
            "updated_at": now_pacific(),
        }).eq("id", user.uid).execute()

        # Handle workspace ownership
        # 1. Get workspaces where user is owner
        owned_ws = supabase.table("tenant_users").select(
            "tenant_id, tenants(settings)"
        ).eq("user_id", user.uid).eq("role", "owner").execute()

        for membership in owned_ws.data or []:
            tenant = membership.get("tenants", {}) or {}
            settings = tenant.get("settings", {}) or {}
            ws_id = membership.get("tenant_id")

            if settings.get("is_personal"):
                # Personal workspace - will be deleted with user
                pass
            else:
                # Non-personal - check for other owners
                other_owners = supabase.table("tenant_users").select(
                    "user_id", count="exact"
                ).eq("tenant_id", ws_id).eq("role", "owner").neq("user_id", user.uid).execute()

                if other_owners.count == 0:
                    # No other owners - check for admins to promote
                    admins = supabase.table("tenant_users").select(
                        "user_id"
                    ).eq("tenant_id", ws_id).eq("role", "admin").limit(1).execute()

                    if admins.data:
                        # Promote first admin to owner
                        new_owner_id = admins.data[0]["user_id"]
                        supabase.table("tenant_users").update({
                            "role": "owner"
                        }).eq("tenant_id", ws_id).eq("user_id", new_owner_id).execute()

        logger.info(f"Scheduled deletion for user {user.uid} on {scheduled_deletion}")

        return APIResponse(
            success=True,
            data=AccountDeleteResponse(
                status="scheduled",
                export_url=export_url,
                scheduled_deletion=scheduled_deletion,
                message="Account scheduled for deletion. You have 30 days to cancel.",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling deletion for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/me/cancel-deletion", response_model=APIResponse[ProfileResponse])
async def cancel_account_deletion(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ProfileResponse]:
    """
    Cancel a scheduled account deletion.

    Only works during the 30-day grace period.

    **Requires:** Valid Firebase JWT
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Check if user has pending deletion
        user_data = await get_user_data(user.uid, supabase)
        if not user_data or user_data.get("status") != "pending_deletion":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending deletion to cancel"
            )

        # Cancel deletion
        supabase.table("users").update({
            "status": "active",
            "scheduled_deletion": None,
            "updated_at": now_pacific(),
        }).eq("id", user.uid).execute()

        # Fetch updated profile
        profile = await build_user_profile(user, supabase)

        logger.info(f"Cancelled deletion for user {user.uid}")

        return APIResponse(
            success=True,
            data=ProfileResponse(
                profile=profile,
                edit_url="/api/profile/me",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling deletion for user {user.uid}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
