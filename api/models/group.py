"""
Groups Models

Pydantic schemas for workspace-scoped groups with hierarchy support.
Groups enable team/department/division organizational structure.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class GroupType(str, Enum):
    """Hierarchy levels for groups."""
    TEAM = "team"
    DEPARTMENT = "department"
    DIVISION = "division"
    CUSTOM = "custom"


class GroupRole(str, Enum):
    """Roles within a group."""
    LEADER = "leader"
    MANAGER = "manager"
    MEMBER = "member"


# === Request Models ===

class GroupCreate(BaseModel):
    """Request model for creating a group."""
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    description: Optional[str] = Field(None, max_length=500, description="Group description")
    group_type: GroupType = Field(default=GroupType.TEAM, description="Hierarchy type")
    parent_group_id: Optional[str] = Field(None, description="Parent group ID for hierarchy")
    settings: Optional[dict] = Field(default_factory=dict, description="Custom group settings")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Engineering Team",
                "description": "Core engineering team",
                "group_type": "team",
                "parent_group_id": "grp_department_123"
            }
        }
    }


class GroupUpdate(BaseModel):
    """Request model for updating a group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New group name")
    description: Optional[str] = Field(None, max_length=500, description="New description")
    group_type: Optional[GroupType] = Field(None, description="New hierarchy type")
    parent_group_id: Optional[str] = Field(None, description="New parent group ID (set to 'null' to make root)")
    settings: Optional[dict] = Field(None, description="Settings to update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Team Name",
                "description": "Updated description"
            }
        }
    }


class GroupMemberAdd(BaseModel):
    """Request model for adding a member to a group."""
    user_id: str = Field(..., description="User ID to add")
    role: GroupRole = Field(default=GroupRole.MEMBER, description="Role in the group")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "firebase_uid_123",
                "role": "member"
            }
        }
    }


class GroupMemberUpdate(BaseModel):
    """Request model for updating a member's role in a group."""
    role: GroupRole = Field(..., description="New role for the member")

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "leader"
            }
        }
    }


class BulkGroupMemberAdd(BaseModel):
    """Request model for adding multiple members to a group."""
    members: List[GroupMemberAdd] = Field(..., min_length=1, description="List of members to add")

    model_config = {
        "json_schema_extra": {
            "example": {
                "members": [
                    {"user_id": "user_1", "role": "member"},
                    {"user_id": "user_2", "role": "leader"}
                ]
            }
        }
    }


# === Response Models ===

class GroupMemberInfo(BaseModel):
    """Information about a group member."""
    user_id: str = Field(..., description="User ID")
    email: Optional[str] = Field(None, description="User's email")
    name: Optional[str] = Field(None, description="User's display name")
    role: GroupRole = Field(..., description="Role in the group")
    joined_at: Optional[str] = Field(None, description="When user joined the group")


class GroupInfo(BaseModel):
    """Full group information."""
    id: str = Field(..., description="Group ID")
    workspace_id: str = Field(..., description="Workspace this group belongs to")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    group_type: GroupType = Field(..., description="Hierarchy type")
    parent_group_id: Optional[str] = Field(None, description="Parent group ID")
    member_count: int = Field(default=0, description="Number of direct members")
    settings: dict = Field(default_factory=dict, description="Group settings")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created the group")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "grp_abc123",
                "workspace_id": "ws_xyz789",
                "name": "Engineering Team",
                "description": "Core engineering team",
                "group_type": "team",
                "parent_group_id": None,
                "member_count": 5,
                "settings": {},
                "created_at": "2025-12-27T10:00:00-08:00",
                "updated_at": "2025-12-27T10:00:00-08:00",
                "created_by": "user_123"
            }
        }
    }


class GroupSummary(BaseModel):
    """Summary info for group listing."""
    id: str = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")
    group_type: GroupType = Field(..., description="Hierarchy type")
    parent_group_id: Optional[str] = Field(None, description="Parent group ID")
    member_count: int = Field(default=0, description="Number of direct members")


class GroupTreeNode(BaseModel):
    """Group with its child groups (for hierarchy display)."""
    id: str = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")
    group_type: GroupType = Field(..., description="Hierarchy type")
    member_count: int = Field(default=0, description="Number of direct members")
    children: List["GroupTreeNode"] = Field(default_factory=list, description="Child groups")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "grp_div_1",
                "name": "Product Division",
                "group_type": "division",
                "member_count": 3,
                "children": [
                    {
                        "id": "grp_dept_1",
                        "name": "Engineering Department",
                        "group_type": "department",
                        "member_count": 2,
                        "children": [
                            {
                                "id": "grp_team_1",
                                "name": "Backend Team",
                                "group_type": "team",
                                "member_count": 5,
                                "children": []
                            }
                        ]
                    }
                ]
            }
        }
    }


# Fix forward reference for recursive model
GroupTreeNode.model_rebuild()


class GroupListResponse(BaseModel):
    """Response for listing groups (flat list)."""
    groups: List[GroupSummary] = Field(..., description="List of groups")
    total: int = Field(..., description="Total count")
    workspace_id: str = Field(..., description="Workspace ID")


class GroupTreeResponse(BaseModel):
    """Response for group hierarchy tree."""
    tree: List[GroupTreeNode] = Field(..., description="Root groups with nested children")
    total_groups: int = Field(..., description="Total number of groups")
    workspace_id: str = Field(..., description="Workspace ID")


class GroupMemberListResponse(BaseModel):
    """Response for listing group members."""
    members: List[GroupMemberInfo] = Field(..., description="List of members")
    total: int = Field(..., description="Total member count")
    group_id: str = Field(..., description="Group ID")


class GroupMemberAddResponse(BaseModel):
    """Response after adding a member."""
    member: GroupMemberInfo = Field(..., description="Added member details")
    group_id: str = Field(..., description="Group ID")
    message: str = Field(..., description="Confirmation message")


class GroupMemberRemoveResponse(BaseModel):
    """Response after removing a member."""
    removed_user_id: str = Field(..., description="ID of removed user")
    group_id: str = Field(..., description="Group ID")
    message: str = Field(..., description="Confirmation message")


class UserGroupsResponse(BaseModel):
    """Response for getting all groups a user belongs to."""
    groups: List[GroupInfo] = Field(..., description="Groups user is a member of")
    total: int = Field(..., description="Total count")
    effective_groups: List[str] = Field(..., description="All group IDs including parent hierarchy (for permissions)")


class GroupCreateResponse(BaseModel):
    """Response after creating a group."""
    group: GroupInfo = Field(..., description="Created group details")
    message: str = Field(..., description="Confirmation message")


class GroupDeleteResponse(BaseModel):
    """Response after deleting a group."""
    deleted_group_id: str = Field(..., description="ID of deleted group")
    orphaned_children: int = Field(default=0, description="Number of child groups that were orphaned")
    message: str = Field(..., description="Confirmation message")
