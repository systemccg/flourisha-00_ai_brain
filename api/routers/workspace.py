"""
Workspace Management Router

Endpoints for workspace CRUD operations.
Workspaces map to tenants in the multi-tenant system.

Acceptance Criteria:
- Personal workspace auto-created on signup
- Switch updates user's active workspace
- Delete requires owner role
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
from models.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceSwitch,
    WorkspaceInfo,
    WorkspaceSummary,
    WorkspaceListResponse,
    WorkspaceSwitchResponse,
    WorkspaceDeleteResponse,
    WorkspaceRole,
    WorkspacePlan,
    WorkspaceMemberInfo,
)
from middleware.auth import get_current_user, UserContext, require_roles
from config import get_settings


router = APIRouter(prefix="/api/workspaces", tags=["Workspaces"])

logger = logging.getLogger("flourisha.api.workspaces")
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Supabase Client ===

def get_supabase():
    """Get Supabase client for workspace operations."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured"
        )

    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_service_key)


# === Helper Functions ===

def generate_workspace_id() -> str:
    """Generate a unique workspace/tenant ID."""
    return f"ws_{uuid.uuid4().hex[:16]}"


def now_pacific() -> str:
    """Get current time in Pacific timezone as ISO string."""
    return datetime.now(PACIFIC).isoformat()


async def get_user_workspaces(user: UserContext, supabase) -> List[dict]:
    """Get all workspaces user belongs to."""
    try:
        # Query tenant_users to get user's workspace memberships
        result = supabase.table("tenant_users").select(
            "tenant_id, role, created_at, tenants(tenant_id, name, settings, created_at)"
        ).eq("user_id", user.uid).execute()

        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching user workspaces: {e}")
        return []


async def get_workspace_by_id(workspace_id: str, supabase) -> Optional[dict]:
    """Get workspace by ID."""
    try:
        result = supabase.table("tenants").select("*").eq("tenant_id", workspace_id).single().execute()
        return result.data
    except Exception as e:
        logger.warning(f"Workspace {workspace_id} not found: {e}")
        return None


async def get_user_role_in_workspace(user_id: str, workspace_id: str, supabase) -> Optional[str]:
    """Get user's role in a specific workspace."""
    try:
        result = supabase.table("tenant_users").select("role").eq(
            "user_id", user_id
        ).eq("tenant_id", workspace_id).single().execute()
        return result.data.get("role") if result.data else None
    except Exception:
        return None


async def get_active_workspace_id(user_id: str, supabase) -> Optional[str]:
    """Get user's currently active workspace ID."""
    try:
        # Check if user_preferences table exists and has active_workspace
        result = supabase.table("user_preferences").select(
            "active_workspace_id"
        ).eq("user_id", user_id).single().execute()
        return result.data.get("active_workspace_id") if result.data else None
    except Exception:
        # If table doesn't exist or no record, return None
        return None


async def set_active_workspace(user_id: str, workspace_id: str, supabase) -> bool:
    """Set user's active workspace."""
    try:
        # Upsert to user_preferences table
        supabase.table("user_preferences").upsert({
            "user_id": user_id,
            "active_workspace_id": workspace_id,
            "updated_at": now_pacific()
        }, on_conflict="user_id").execute()
        return True
    except Exception as e:
        logger.error(f"Error setting active workspace: {e}")
        return False


async def get_workspace_member_count(workspace_id: str, supabase) -> int:
    """Get count of members in a workspace."""
    try:
        result = supabase.table("tenant_users").select(
            "user_id", count="exact"
        ).eq("tenant_id", workspace_id).execute()
        return result.count or 1
    except Exception:
        return 1


def workspace_to_info(
    workspace: dict,
    role: WorkspaceRole = WorkspaceRole.MEMBER,
    member_count: int = 1,
    is_active: bool = False
) -> WorkspaceInfo:
    """Convert database workspace record to WorkspaceInfo model."""
    settings = workspace.get("settings", {}) or {}
    return WorkspaceInfo(
        id=workspace.get("tenant_id", ""),
        name=workspace.get("name", "Unknown"),
        description=settings.get("description"),
        is_personal=settings.get("is_personal", False),
        owner_id=workspace.get("owner_id", ""),
        plan=WorkspacePlan(settings.get("plan", "free")),
        member_count=member_count,
        settings=settings,
        created_at=workspace.get("created_at"),
        updated_at=workspace.get("updated_at"),
    )


# === Endpoints ===

@router.get("/", response_model=APIResponse[WorkspaceListResponse])
async def list_workspaces(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceListResponse]:
    """
    List all workspaces the user belongs to.

    Returns workspaces where user is a member, admin, or owner.
    Includes the currently active workspace indicator.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Get user's workspace memberships
        memberships = await get_user_workspaces(user, supabase)
        active_workspace_id = await get_active_workspace_id(user.uid, supabase)

        workspaces = []
        for membership in memberships:
            tenant_data = membership.get("tenants", {}) or {}
            workspace_id = membership.get("tenant_id") or tenant_data.get("tenant_id")

            if not workspace_id:
                continue

            settings = tenant_data.get("settings", {}) or {}
            member_count = await get_workspace_member_count(workspace_id, supabase)

            workspaces.append(WorkspaceSummary(
                id=workspace_id,
                name=tenant_data.get("name", "Unknown"),
                is_personal=settings.get("is_personal", False),
                role=WorkspaceRole(membership.get("role", "member")),
                member_count=member_count,
                is_active=(workspace_id == active_workspace_id),
            ))

        return APIResponse(
            success=True,
            data=WorkspaceListResponse(
                workspaces=workspaces,
                total=len(workspaces),
                active_workspace_id=active_workspace_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error listing workspaces: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/active", response_model=APIResponse[WorkspaceInfo])
async def get_active_workspace(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceInfo]:
    """
    Get the user's currently active workspace.

    If no active workspace is set, returns the user's personal workspace
    or first available workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        active_id = await get_active_workspace_id(user.uid, supabase)

        if active_id:
            workspace = await get_workspace_by_id(active_id, supabase)
            if workspace:
                role = await get_user_role_in_workspace(user.uid, active_id, supabase)
                member_count = await get_workspace_member_count(active_id, supabase)
                return APIResponse(
                    success=True,
                    data=workspace_to_info(
                        workspace,
                        role=WorkspaceRole(role or "member"),
                        member_count=member_count,
                        is_active=True,
                    ),
                    meta=ResponseMeta(**meta_dict),
                )

        # No active workspace set - get first available
        memberships = await get_user_workspaces(user, supabase)
        if memberships:
            first = memberships[0]
            tenant_data = first.get("tenants", {}) or {}
            workspace_id = first.get("tenant_id") or tenant_data.get("tenant_id")

            if workspace_id:
                # Set this as active
                await set_active_workspace(user.uid, workspace_id, supabase)
                workspace = await get_workspace_by_id(workspace_id, supabase)
                if workspace:
                    member_count = await get_workspace_member_count(workspace_id, supabase)
                    return APIResponse(
                        success=True,
                        data=workspace_to_info(
                            workspace,
                            role=WorkspaceRole(first.get("role", "member")),
                            member_count=member_count,
                            is_active=True,
                        ),
                        meta=ResponseMeta(**meta_dict),
                    )

        return APIResponse(
            success=False,
            error="No workspace found. Please create a workspace first.",
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error getting active workspace: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{workspace_id}", response_model=APIResponse[WorkspaceInfo])
async def get_workspace(
    workspace_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceInfo]:
    """
    Get details of a specific workspace.

    User must be a member of the workspace to view it.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify user has access
        role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )

        workspace = await get_workspace_by_id(workspace_id, supabase)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found"
            )

        active_id = await get_active_workspace_id(user.uid, supabase)
        member_count = await get_workspace_member_count(workspace_id, supabase)

        return APIResponse(
            success=True,
            data=workspace_to_info(
                workspace,
                role=WorkspaceRole(role),
                member_count=member_count,
                is_active=(workspace_id == active_id),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workspace {workspace_id}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/", response_model=APIResponse[WorkspaceInfo], status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceInfo]:
    """
    Create a new workspace.

    The creating user becomes the owner of the workspace.
    Personal workspaces are auto-created on signup (handled separately).
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        workspace_id = generate_workspace_id()
        now = now_pacific()

        # Create tenant record
        tenant_data = {
            "tenant_id": workspace_id,
            "name": workspace_data.name,
            "owner_id": user.uid,
            "settings": {
                "description": workspace_data.description,
                "is_personal": workspace_data.is_personal,
                "plan": "free",
            },
            "created_at": now,
            "updated_at": now,
        }

        supabase.table("tenants").insert(tenant_data).execute()

        # Add creator as owner in tenant_users
        supabase.table("tenant_users").insert({
            "tenant_id": workspace_id,
            "user_id": user.uid,
            "role": "owner",
            "groups": [],
            "created_at": now,
        }).execute()

        # Set as active workspace if user has none
        current_active = await get_active_workspace_id(user.uid, supabase)
        if not current_active:
            await set_active_workspace(user.uid, workspace_id, supabase)

        logger.info(f"Created workspace {workspace_id} for user {user.uid}")

        return APIResponse(
            success=True,
            data=WorkspaceInfo(
                id=workspace_id,
                name=workspace_data.name,
                description=workspace_data.description,
                is_personal=workspace_data.is_personal,
                owner_id=user.uid,
                plan=WorkspacePlan.FREE,
                member_count=1,
                settings=tenant_data["settings"],
                created_at=now,
                updated_at=now,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/personal", response_model=APIResponse[WorkspaceInfo], status_code=status.HTTP_201_CREATED)
async def create_personal_workspace(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceInfo]:
    """
    Create a personal workspace for the user.

    This is typically called during signup to auto-create
    the user's personal workspace. Returns existing if one exists.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Check if user already has a personal workspace
        memberships = await get_user_workspaces(user, supabase)
        for membership in memberships:
            tenant_data = membership.get("tenants", {}) or {}
            settings = tenant_data.get("settings", {}) or {}
            if settings.get("is_personal"):
                # Return existing personal workspace
                workspace_id = membership.get("tenant_id") or tenant_data.get("tenant_id")
                member_count = await get_workspace_member_count(workspace_id, supabase)
                return APIResponse(
                    success=True,
                    data=workspace_to_info(
                        tenant_data,
                        role=WorkspaceRole(membership.get("role", "owner")),
                        member_count=member_count,
                    ),
                    meta=ResponseMeta(**meta_dict),
                )

        # Create new personal workspace
        workspace_id = generate_workspace_id()
        now = now_pacific()
        display_name = user.name or user.email or "Personal"

        tenant_data = {
            "tenant_id": workspace_id,
            "name": f"{display_name}'s Workspace",
            "owner_id": user.uid,
            "settings": {
                "description": "Personal workspace",
                "is_personal": True,
                "plan": "free",
            },
            "created_at": now,
            "updated_at": now,
        }

        supabase.table("tenants").insert(tenant_data).execute()

        supabase.table("tenant_users").insert({
            "tenant_id": workspace_id,
            "user_id": user.uid,
            "role": "owner",
            "groups": [],
            "created_at": now,
        }).execute()

        # Set as active workspace
        await set_active_workspace(user.uid, workspace_id, supabase)

        logger.info(f"Created personal workspace {workspace_id} for user {user.uid}")

        return APIResponse(
            success=True,
            data=WorkspaceInfo(
                id=workspace_id,
                name=tenant_data["name"],
                description="Personal workspace",
                is_personal=True,
                owner_id=user.uid,
                plan=WorkspacePlan.FREE,
                member_count=1,
                settings=tenant_data["settings"],
                created_at=now,
                updated_at=now,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error creating personal workspace: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.patch("/{workspace_id}", response_model=APIResponse[WorkspaceInfo])
async def update_workspace(
    workspace_id: str,
    updates: WorkspaceUpdate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceInfo]:
    """
    Update workspace details.

    Only owners and admins can update workspace settings.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify user has admin/owner access
        role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can update workspace settings"
            )

        workspace = await get_workspace_by_id(workspace_id, supabase)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found"
            )

        # Build update payload
        update_data = {"updated_at": now_pacific()}

        if updates.name:
            update_data["name"] = updates.name

        if updates.description is not None or updates.settings:
            current_settings = workspace.get("settings", {}) or {}
            if updates.description is not None:
                current_settings["description"] = updates.description
            if updates.settings:
                current_settings.update(updates.settings)
            update_data["settings"] = current_settings

        # Perform update
        supabase.table("tenants").update(update_data).eq("tenant_id", workspace_id).execute()

        # Fetch updated workspace
        updated = await get_workspace_by_id(workspace_id, supabase)
        active_id = await get_active_workspace_id(user.uid, supabase)
        member_count = await get_workspace_member_count(workspace_id, supabase)

        logger.info(f"Updated workspace {workspace_id}")

        return APIResponse(
            success=True,
            data=workspace_to_info(
                updated,
                role=WorkspaceRole(role),
                member_count=member_count,
                is_active=(workspace_id == active_id),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workspace {workspace_id}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/switch", response_model=APIResponse[WorkspaceSwitchResponse])
async def switch_workspace(
    switch_data: WorkspaceSwitch,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceSwitchResponse]:
    """
    Switch to a different workspace.

    Updates the user's active workspace. User must be a member
    of the target workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        target_id = switch_data.workspace_id

        # Verify user has access to target workspace
        role = await get_user_role_in_workspace(user.uid, target_id, supabase)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )

        workspace = await get_workspace_by_id(target_id, supabase)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {target_id} not found"
            )

        # Get previous active workspace
        previous_id = await get_active_workspace_id(user.uid, supabase)

        # Set new active workspace
        success = await set_active_workspace(user.uid, target_id, supabase)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to switch workspace"
            )

        member_count = await get_workspace_member_count(target_id, supabase)

        logger.info(f"User {user.uid} switched from {previous_id} to {target_id}")

        return APIResponse(
            success=True,
            data=WorkspaceSwitchResponse(
                previous_workspace_id=previous_id,
                current_workspace_id=target_id,
                workspace=workspace_to_info(
                    workspace,
                    role=WorkspaceRole(role),
                    member_count=member_count,
                    is_active=True,
                ),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching workspace: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/{workspace_id}", response_model=APIResponse[WorkspaceDeleteResponse])
async def delete_workspace(
    workspace_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkspaceDeleteResponse]:
    """
    Delete a workspace.

    REQUIRES OWNER ROLE. Cannot delete personal workspace.
    If deleting active workspace, switches to another available workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify user is owner
        role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owners can delete workspaces"
            )

        workspace = await get_workspace_by_id(workspace_id, supabase)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found"
            )

        # Cannot delete personal workspace
        settings = workspace.get("settings", {}) or {}
        if settings.get("is_personal"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete personal workspace"
            )

        # Check if this is the active workspace
        active_id = await get_active_workspace_id(user.uid, supabase)

        # Delete workspace (cascade will handle tenant_users)
        supabase.table("tenants").delete().eq("tenant_id", workspace_id).execute()

        # If we deleted the active workspace, switch to another
        fallback_id = None
        if active_id == workspace_id:
            memberships = await get_user_workspaces(user, supabase)
            if memberships:
                fallback = memberships[0]
                fallback_id = fallback.get("tenant_id") or fallback.get("tenants", {}).get("tenant_id")
                if fallback_id:
                    await set_active_workspace(user.uid, fallback_id, supabase)

        logger.info(f"Deleted workspace {workspace_id} by owner {user.uid}")

        return APIResponse(
            success=True,
            data=WorkspaceDeleteResponse(
                deleted_workspace_id=workspace_id,
                fallback_workspace_id=fallback_id,
                message=f"Workspace '{workspace.get('name', workspace_id)}' has been deleted",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workspace {workspace_id}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
