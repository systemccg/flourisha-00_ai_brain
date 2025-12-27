"""
Workspace Models

Pydantic schemas for workspace management API.
Workspaces map to tenants in the multi-tenant system.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class WorkspaceRole(str, Enum):
    """Roles within a workspace."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspacePlan(str, Enum):
    """Workspace billing plans."""
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


# === Request Models ===

class WorkspaceCreate(BaseModel):
    """Request model for creating a workspace."""
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, max_length=500, description="Workspace description")
    is_personal: bool = Field(default=False, description="Whether this is a personal workspace")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "My Team Workspace",
                "description": "Collaboration space for the engineering team",
                "is_personal": False
            }
        }
    }


class WorkspaceUpdate(BaseModel):
    """Request model for updating a workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New workspace name")
    description: Optional[str] = Field(None, max_length=500, description="New description")
    settings: Optional[dict] = Field(None, description="Workspace settings to update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Workspace Name",
                "description": "Updated description"
            }
        }
    }


class WorkspaceSwitch(BaseModel):
    """Request model for switching active workspace."""
    workspace_id: str = Field(..., description="ID of workspace to switch to")

    model_config = {
        "json_schema_extra": {
            "example": {
                "workspace_id": "ws_abc123"
            }
        }
    }


# === Response Models ===

class WorkspaceMemberInfo(BaseModel):
    """Information about a workspace member."""
    user_id: str = Field(..., description="User's Firebase UID")
    email: Optional[str] = Field(None, description="User's email")
    name: Optional[str] = Field(None, description="User's display name")
    role: WorkspaceRole = Field(..., description="User's role in workspace")
    joined_at: Optional[str] = Field(None, description="When user joined")


class WorkspaceInfo(BaseModel):
    """Full workspace information."""
    id: str = Field(..., description="Workspace ID (tenant_id)")
    name: str = Field(..., description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    is_personal: bool = Field(default=False, description="Whether this is a personal workspace")
    owner_id: str = Field(..., description="Owner's user ID")
    plan: WorkspacePlan = Field(default=WorkspacePlan.FREE, description="Current billing plan")
    member_count: int = Field(default=1, description="Number of members")
    settings: dict = Field(default_factory=dict, description="Workspace settings")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "tenant_abc123",
                "name": "Personal Workspace",
                "description": "My personal workspace",
                "is_personal": True,
                "owner_id": "user_xyz",
                "plan": "free",
                "member_count": 1,
                "settings": {},
                "created_at": "2025-12-24T10:00:00-08:00",
                "updated_at": "2025-12-24T10:00:00-08:00"
            }
        }
    }


class WorkspaceSummary(BaseModel):
    """Summary info for workspace listing."""
    id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Workspace name")
    is_personal: bool = Field(default=False, description="Whether personal workspace")
    role: WorkspaceRole = Field(..., description="User's role in this workspace")
    member_count: int = Field(default=1, description="Number of members")
    is_active: bool = Field(default=False, description="Whether this is user's active workspace")


class WorkspaceListResponse(BaseModel):
    """Response for listing user's workspaces."""
    workspaces: List[WorkspaceSummary] = Field(..., description="List of workspaces")
    total: int = Field(..., description="Total count")
    active_workspace_id: Optional[str] = Field(None, description="Currently active workspace ID")


class WorkspaceSwitchResponse(BaseModel):
    """Response after switching workspaces."""
    previous_workspace_id: Optional[str] = Field(None, description="Previous active workspace")
    current_workspace_id: str = Field(..., description="New active workspace")
    workspace: WorkspaceInfo = Field(..., description="Full info of new active workspace")


class WorkspaceDeleteResponse(BaseModel):
    """Response after deleting a workspace."""
    deleted_workspace_id: str = Field(..., description="ID of deleted workspace")
    fallback_workspace_id: Optional[str] = Field(None, description="New active workspace after deletion")
    message: str = Field(..., description="Confirmation message")
