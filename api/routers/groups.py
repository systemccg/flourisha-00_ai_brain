"""
Groups Router

Endpoints for workspace-scoped group management with hierarchy support.
Groups enable team/department/division organizational structure.

Acceptance Criteria:
- Tree structure via parent_group_id
- Hierarchy types: team, department, division
- Member access is union of all groups
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
from models.group import (
    GroupCreate,
    GroupUpdate,
    GroupMemberAdd,
    GroupMemberUpdate,
    BulkGroupMemberAdd,
    GroupInfo,
    GroupSummary,
    GroupTreeNode,
    GroupListResponse,
    GroupTreeResponse,
    GroupMemberInfo,
    GroupMemberListResponse,
    GroupMemberAddResponse,
    GroupMemberRemoveResponse,
    UserGroupsResponse,
    GroupCreateResponse,
    GroupDeleteResponse,
    GroupType,
    GroupRole,
)
from middleware.auth import get_current_user, UserContext, require_roles
from config import get_settings


router = APIRouter(prefix="/api/groups", tags=["Groups"])

logger = logging.getLogger("flourisha.api.groups")
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Supabase Client ===

def get_supabase():
    """Get Supabase client for group operations."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured"
        )

    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_service_key)


# === Helper Functions ===

def generate_group_id() -> str:
    """Generate a unique group ID."""
    return f"grp_{uuid.uuid4().hex[:16]}"


def now_pacific() -> str:
    """Get current time in Pacific timezone as ISO string."""
    return datetime.now(PACIFIC).isoformat()


async def get_user_workspace_id(user: UserContext, supabase) -> Optional[str]:
    """Get user's active workspace ID."""
    try:
        result = supabase.table("user_preferences").select(
            "active_workspace_id"
        ).eq("user_id", user.uid).single().execute()
        return result.data.get("active_workspace_id") if result.data else None
    except Exception:
        # Try to get from tenant_users if no preference set
        try:
            result = supabase.table("tenant_users").select(
                "tenant_id"
            ).eq("user_id", user.uid).limit(1).execute()
            return result.data[0].get("tenant_id") if result.data else None
        except Exception:
            return None


async def user_can_manage_groups(user: UserContext, workspace_id: str, supabase) -> bool:
    """Check if user has permission to manage groups in workspace."""
    try:
        result = supabase.table("tenant_users").select("role").eq(
            "user_id", user.uid
        ).eq("tenant_id", workspace_id).single().execute()

        if result.data:
            role = result.data.get("role", "")
            return role in ["owner", "admin"]
        return False
    except Exception:
        return False


async def get_group_by_id(group_id: str, supabase) -> Optional[dict]:
    """Get group by ID."""
    try:
        result = supabase.table("groups").select("*").eq("id", group_id).single().execute()
        return result.data
    except Exception:
        return None


async def get_group_member_count(group_id: str, supabase) -> int:
    """Get count of members in a group."""
    try:
        result = supabase.table("group_members").select(
            "user_id", count="exact"
        ).eq("group_id", group_id).execute()
        return result.count or 0
    except Exception:
        return 0


async def get_all_ancestor_groups(group_id: str, supabase) -> List[str]:
    """Get all ancestor group IDs (parent, grandparent, etc.)."""
    ancestors = []
    current_id = group_id

    # Prevent infinite loops with max depth
    max_depth = 10
    depth = 0

    while current_id and depth < max_depth:
        group = await get_group_by_id(current_id, supabase)
        if not group:
            break
        parent_id = group.get("parent_group_id")
        if parent_id:
            ancestors.append(parent_id)
            current_id = parent_id
        else:
            break
        depth += 1

    return ancestors


def group_to_info(group: dict, member_count: int = 0) -> GroupInfo:
    """Convert database group record to GroupInfo model."""
    return GroupInfo(
        id=group.get("id", ""),
        workspace_id=group.get("workspace_id", ""),
        name=group.get("name", "Unknown"),
        description=group.get("description"),
        group_type=GroupType(group.get("group_type", "team")),
        parent_group_id=group.get("parent_group_id"),
        member_count=member_count,
        settings=group.get("settings", {}) or {},
        created_at=group.get("created_at"),
        updated_at=group.get("updated_at"),
        created_by=group.get("created_by"),
    )


def group_to_summary(group: dict, member_count: int = 0) -> GroupSummary:
    """Convert database group record to GroupSummary model."""
    return GroupSummary(
        id=group.get("id", ""),
        name=group.get("name", "Unknown"),
        group_type=GroupType(group.get("group_type", "team")),
        parent_group_id=group.get("parent_group_id"),
        member_count=member_count,
    )


async def build_group_tree(workspace_id: str, supabase) -> List[GroupTreeNode]:
    """Build hierarchical tree of groups for a workspace."""
    try:
        # Get all groups for workspace
        result = supabase.table("groups").select("*").eq(
            "workspace_id", workspace_id
        ).execute()

        groups = result.data or []

        # Get member counts for all groups
        member_counts = {}
        for group in groups:
            member_counts[group["id"]] = await get_group_member_count(group["id"], supabase)

        # Build lookup dictionary
        group_dict = {g["id"]: g for g in groups}

        # Build tree nodes
        def build_node(group: dict) -> GroupTreeNode:
            children = [
                build_node(g) for g in groups
                if g.get("parent_group_id") == group["id"]
            ]
            return GroupTreeNode(
                id=group["id"],
                name=group["name"],
                group_type=GroupType(group.get("group_type", "team")),
                member_count=member_counts.get(group["id"], 0),
                children=children,
            )

        # Get root groups (no parent)
        root_groups = [g for g in groups if not g.get("parent_group_id")]

        return [build_node(g) for g in root_groups]

    except Exception as e:
        logger.error(f"Error building group tree: {e}")
        return []


# === Endpoints ===

@router.get("/", response_model=APIResponse[GroupListResponse])
async def list_groups(
    request: Request,
    workspace_id: Optional[str] = None,
    group_type: Optional[GroupType] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupListResponse]:
    """
    List all groups in a workspace.

    Returns flat list of groups. Use /tree endpoint for hierarchical view.
    Filters by group_type if provided.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Get workspace ID
        ws_id = workspace_id or await get_user_workspace_id(user, supabase)
        if not ws_id:
            return APIResponse(
                success=False,
                error="No active workspace. Please select a workspace first.",
                meta=ResponseMeta(**meta_dict),
            )

        # Build query
        query = supabase.table("groups").select("*").eq("workspace_id", ws_id)

        if group_type:
            query = query.eq("group_type", group_type.value)

        result = query.order("name").execute()
        groups_data = result.data or []

        # Get member counts
        groups = []
        for group in groups_data:
            member_count = await get_group_member_count(group["id"], supabase)
            groups.append(group_to_summary(group, member_count))

        return APIResponse(
            success=True,
            data=GroupListResponse(
                groups=groups,
                total=len(groups),
                workspace_id=ws_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error listing groups: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/tree", response_model=APIResponse[GroupTreeResponse])
async def get_group_tree(
    request: Request,
    workspace_id: Optional[str] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupTreeResponse]:
    """
    Get hierarchical tree of groups in a workspace.

    Returns nested tree structure with parent-child relationships.
    Root groups have no parent_group_id.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        ws_id = workspace_id or await get_user_workspace_id(user, supabase)
        if not ws_id:
            return APIResponse(
                success=False,
                error="No active workspace. Please select a workspace first.",
                meta=ResponseMeta(**meta_dict),
            )

        tree = await build_group_tree(ws_id, supabase)

        # Count total groups
        def count_nodes(nodes: List[GroupTreeNode]) -> int:
            return sum(1 + count_nodes(n.children) for n in nodes)

        total = count_nodes(tree)

        return APIResponse(
            success=True,
            data=GroupTreeResponse(
                tree=tree,
                total_groups=total,
                workspace_id=ws_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error getting group tree: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/my-groups", response_model=APIResponse[UserGroupsResponse])
async def get_my_groups(
    request: Request,
    workspace_id: Optional[str] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[UserGroupsResponse]:
    """
    Get all groups the current user belongs to.

    Returns both direct memberships and effective groups (including parent hierarchy).
    Effective groups are used for permission calculations.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        ws_id = workspace_id or await get_user_workspace_id(user, supabase)
        if not ws_id:
            return APIResponse(
                success=False,
                error="No active workspace. Please select a workspace first.",
                meta=ResponseMeta(**meta_dict),
            )

        # Get user's direct group memberships
        result = supabase.table("group_members").select(
            "group_id, role, joined_at, groups(*)"
        ).eq("user_id", user.uid).execute()

        memberships = result.data or []

        groups = []
        effective_group_ids = set()

        for membership in memberships:
            group_data = membership.get("groups", {})
            if group_data and group_data.get("workspace_id") == ws_id:
                group_id = group_data["id"]
                member_count = await get_group_member_count(group_id, supabase)
                groups.append(group_to_info(group_data, member_count))

                # Add this group and all ancestors to effective groups
                effective_group_ids.add(group_id)
                ancestors = await get_all_ancestor_groups(group_id, supabase)
                effective_group_ids.update(ancestors)

        return APIResponse(
            success=True,
            data=UserGroupsResponse(
                groups=groups,
                total=len(groups),
                effective_groups=list(effective_group_ids),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error getting user groups: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{group_id}", response_model=APIResponse[GroupInfo])
async def get_group(
    group_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupInfo]:
    """
    Get details of a specific group.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        member_count = await get_group_member_count(group_id, supabase)

        return APIResponse(
            success=True,
            data=group_to_info(group, member_count),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error getting group: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/", response_model=APIResponse[GroupCreateResponse])
async def create_group(
    group_data: GroupCreate,
    request: Request,
    workspace_id: Optional[str] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupCreateResponse]:
    """
    Create a new group in a workspace.

    Requires admin or owner role in the workspace.
    Set parent_group_id to create as child of another group.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        ws_id = workspace_id or await get_user_workspace_id(user, supabase)
        if not ws_id:
            return APIResponse(
                success=False,
                error="No active workspace. Please select a workspace first.",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, ws_id, supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to create groups",
                meta=ResponseMeta(**meta_dict),
            )

        # Validate parent group if specified
        if group_data.parent_group_id:
            parent = await get_group_by_id(group_data.parent_group_id, supabase)
            if not parent:
                return APIResponse(
                    success=False,
                    error=f"Parent group {group_data.parent_group_id} not found",
                    meta=ResponseMeta(**meta_dict),
                )
            if parent.get("workspace_id") != ws_id:
                return APIResponse(
                    success=False,
                    error="Parent group must be in the same workspace",
                    meta=ResponseMeta(**meta_dict),
                )

        # Create group
        group_id = generate_group_id()
        now = now_pacific()

        new_group = {
            "id": group_id,
            "workspace_id": ws_id,
            "name": group_data.name,
            "description": group_data.description,
            "group_type": group_data.group_type.value,
            "parent_group_id": group_data.parent_group_id,
            "settings": group_data.settings or {},
            "created_at": now,
            "updated_at": now,
            "created_by": user.uid,
        }

        result = supabase.table("groups").insert(new_group).execute()

        if not result.data:
            return APIResponse(
                success=False,
                error="Failed to create group",
                meta=ResponseMeta(**meta_dict),
            )

        return APIResponse(
            success=True,
            data=GroupCreateResponse(
                group=group_to_info(result.data[0], 0),
                message=f"Group '{group_data.name}' created successfully",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error creating group: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/{group_id}", response_model=APIResponse[GroupInfo])
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupInfo]:
    """
    Update a group's details.

    Requires admin or owner role in the workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Get existing group
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, group["workspace_id"], supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to update groups",
                meta=ResponseMeta(**meta_dict),
            )

        # Validate new parent if specified
        if group_data.parent_group_id and group_data.parent_group_id != "null":
            parent = await get_group_by_id(group_data.parent_group_id, supabase)
            if not parent:
                return APIResponse(
                    success=False,
                    error=f"Parent group {group_data.parent_group_id} not found",
                    meta=ResponseMeta(**meta_dict),
                )
            if parent.get("workspace_id") != group["workspace_id"]:
                return APIResponse(
                    success=False,
                    error="Parent group must be in the same workspace",
                    meta=ResponseMeta(**meta_dict),
                )
            # Prevent circular reference
            if group_data.parent_group_id == group_id:
                return APIResponse(
                    success=False,
                    error="A group cannot be its own parent",
                    meta=ResponseMeta(**meta_dict),
                )

        # Build update dict
        updates = {"updated_at": now_pacific()}

        if group_data.name is not None:
            updates["name"] = group_data.name
        if group_data.description is not None:
            updates["description"] = group_data.description
        if group_data.group_type is not None:
            updates["group_type"] = group_data.group_type.value
        if group_data.parent_group_id is not None:
            updates["parent_group_id"] = None if group_data.parent_group_id == "null" else group_data.parent_group_id
        if group_data.settings is not None:
            updates["settings"] = {**group.get("settings", {}), **group_data.settings}

        result = supabase.table("groups").update(updates).eq("id", group_id).execute()

        if not result.data:
            return APIResponse(
                success=False,
                error="Failed to update group",
                meta=ResponseMeta(**meta_dict),
            )

        member_count = await get_group_member_count(group_id, supabase)

        return APIResponse(
            success=True,
            data=group_to_info(result.data[0], member_count),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error updating group: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/{group_id}", response_model=APIResponse[GroupDeleteResponse])
async def delete_group(
    group_id: str,
    request: Request,
    orphan_children: bool = True,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupDeleteResponse]:
    """
    Delete a group.

    Requires admin or owner role in the workspace.
    By default, child groups are orphaned (moved to root level).
    Set orphan_children=false to also delete children (cascade).
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Get existing group
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, group["workspace_id"], supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to delete groups",
                meta=ResponseMeta(**meta_dict),
            )

        # Handle child groups
        children_result = supabase.table("groups").select("id").eq(
            "parent_group_id", group_id
        ).execute()
        children = children_result.data or []
        orphaned_count = len(children)

        if children:
            if orphan_children:
                # Move children to root (remove parent)
                supabase.table("groups").update({
                    "parent_group_id": None,
                    "updated_at": now_pacific()
                }).eq("parent_group_id", group_id).execute()
            else:
                # Cascade delete - recursively delete children
                for child in children:
                    await delete_group_recursive(child["id"], supabase)

        # Delete group members first
        supabase.table("group_members").delete().eq("group_id", group_id).execute()

        # Delete the group
        supabase.table("groups").delete().eq("id", group_id).execute()

        return APIResponse(
            success=True,
            data=GroupDeleteResponse(
                deleted_group_id=group_id,
                orphaned_children=orphaned_count if orphan_children else 0,
                message=f"Group deleted successfully",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


async def delete_group_recursive(group_id: str, supabase):
    """Recursively delete a group and all its children."""
    # Get children first
    children_result = supabase.table("groups").select("id").eq(
        "parent_group_id", group_id
    ).execute()

    # Delete children recursively
    for child in children_result.data or []:
        await delete_group_recursive(child["id"], supabase)

    # Delete members
    supabase.table("group_members").delete().eq("group_id", group_id).execute()

    # Delete group
    supabase.table("groups").delete().eq("id", group_id).execute()


# === Member Management Endpoints ===

@router.get("/{group_id}/members", response_model=APIResponse[GroupMemberListResponse])
async def list_group_members(
    group_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupMemberListResponse]:
    """
    List all members of a group.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify group exists
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Get members
        result = supabase.table("group_members").select("*").eq(
            "group_id", group_id
        ).execute()

        memberships = result.data or []

        # Build member info list
        members = []
        for m in memberships:
            # Try to get user details
            user_result = supabase.table("users").select(
                "email, display_name"
            ).eq("id", m["user_id"]).single().execute()

            user_data = user_result.data or {}

            members.append(GroupMemberInfo(
                user_id=m["user_id"],
                email=user_data.get("email"),
                name=user_data.get("display_name"),
                role=GroupRole(m.get("role", "member")),
                joined_at=m.get("joined_at"),
            ))

        return APIResponse(
            success=True,
            data=GroupMemberListResponse(
                members=members,
                total=len(members),
                group_id=group_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error listing group members: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/{group_id}/members", response_model=APIResponse[GroupMemberAddResponse])
async def add_group_member(
    group_id: str,
    member_data: GroupMemberAdd,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupMemberAddResponse]:
    """
    Add a member to a group.

    Requires admin or owner role in the workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify group exists
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, group["workspace_id"], supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to manage group members",
                meta=ResponseMeta(**meta_dict),
            )

        # Check if user is already a member
        existing = supabase.table("group_members").select("id").eq(
            "group_id", group_id
        ).eq("user_id", member_data.user_id).execute()

        if existing.data:
            return APIResponse(
                success=False,
                error="User is already a member of this group",
                meta=ResponseMeta(**meta_dict),
            )

        # Add member
        now = now_pacific()
        new_member = {
            "group_id": group_id,
            "user_id": member_data.user_id,
            "role": member_data.role.value,
            "joined_at": now,
        }

        result = supabase.table("group_members").insert(new_member).execute()

        if not result.data:
            return APIResponse(
                success=False,
                error="Failed to add member",
                meta=ResponseMeta(**meta_dict),
            )

        # Get user details for response
        user_result = supabase.table("users").select(
            "email, display_name"
        ).eq("id", member_data.user_id).single().execute()

        user_data = user_result.data or {}

        return APIResponse(
            success=True,
            data=GroupMemberAddResponse(
                member=GroupMemberInfo(
                    user_id=member_data.user_id,
                    email=user_data.get("email"),
                    name=user_data.get("display_name"),
                    role=member_data.role,
                    joined_at=now,
                ),
                group_id=group_id,
                message="Member added successfully",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error adding group member: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/{group_id}/members/bulk", response_model=APIResponse[dict])
async def add_bulk_group_members(
    group_id: str,
    bulk_data: BulkGroupMemberAdd,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Add multiple members to a group at once.

    Requires admin or owner role in the workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify group exists
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, group["workspace_id"], supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to manage group members",
                meta=ResponseMeta(**meta_dict),
            )

        now = now_pacific()
        added = 0
        skipped = 0

        for member in bulk_data.members:
            # Check if already exists
            existing = supabase.table("group_members").select("id").eq(
                "group_id", group_id
            ).eq("user_id", member.user_id).execute()

            if existing.data:
                skipped += 1
                continue

            # Add member
            supabase.table("group_members").insert({
                "group_id": group_id,
                "user_id": member.user_id,
                "role": member.role.value,
                "joined_at": now,
            }).execute()
            added += 1

        return APIResponse(
            success=True,
            data={
                "added": added,
                "skipped": skipped,
                "total_requested": len(bulk_data.members),
                "group_id": group_id,
            },
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error adding bulk group members: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/{group_id}/members/{member_user_id}", response_model=APIResponse[GroupMemberInfo])
async def update_group_member(
    group_id: str,
    member_user_id: str,
    member_data: GroupMemberUpdate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupMemberInfo]:
    """
    Update a member's role in a group.

    Requires admin or owner role in the workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify group exists
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, group["workspace_id"], supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to manage group members",
                meta=ResponseMeta(**meta_dict),
            )

        # Update member role
        result = supabase.table("group_members").update({
            "role": member_data.role.value
        }).eq("group_id", group_id).eq("user_id", member_user_id).execute()

        if not result.data:
            return APIResponse(
                success=False,
                error="Member not found in group",
                meta=ResponseMeta(**meta_dict),
            )

        # Get updated member info
        member = result.data[0]
        user_result = supabase.table("users").select(
            "email, display_name"
        ).eq("id", member_user_id).single().execute()

        user_data = user_result.data or {}

        return APIResponse(
            success=True,
            data=GroupMemberInfo(
                user_id=member_user_id,
                email=user_data.get("email"),
                name=user_data.get("display_name"),
                role=member_data.role,
                joined_at=member.get("joined_at"),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error updating group member: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/{group_id}/members/{member_user_id}", response_model=APIResponse[GroupMemberRemoveResponse])
async def remove_group_member(
    group_id: str,
    member_user_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GroupMemberRemoveResponse]:
    """
    Remove a member from a group.

    Requires admin or owner role in the workspace.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify group exists
        group = await get_group_by_id(group_id, supabase)
        if not group:
            return APIResponse(
                success=False,
                error=f"Group {group_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Check permissions
        if not await user_can_manage_groups(user, group["workspace_id"], supabase):
            return APIResponse(
                success=False,
                error="Insufficient permissions to manage group members",
                meta=ResponseMeta(**meta_dict),
            )

        # Remove member
        result = supabase.table("group_members").delete().eq(
            "group_id", group_id
        ).eq("user_id", member_user_id).execute()

        if not result.data:
            return APIResponse(
                success=False,
                error="Member not found in group",
                meta=ResponseMeta(**meta_dict),
            )

        return APIResponse(
            success=True,
            data=GroupMemberRemoveResponse(
                removed_user_id=member_user_id,
                group_id=group_id,
                message="Member removed from group",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error removing group member: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
