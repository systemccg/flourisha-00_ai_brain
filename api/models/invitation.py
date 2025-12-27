"""
Invitation Models

Pydantic schemas for workspace invitation system.
Enables secure workspace access via unique invitation tokens.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

from models.workspace import WorkspaceRole


class InvitationStatus(str, Enum):
    """Status of an invitation."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# === Request Models ===

class InvitationCreate(BaseModel):
    """Request model for creating an invitation."""
    email: EmailStr = Field(..., description="Email address to invite")
    role: WorkspaceRole = Field(
        default=WorkspaceRole.MEMBER,
        description="Role to assign when invitation is accepted"
    )
    expires_in_hours: int = Field(
        default=168,  # 7 days
        ge=1,
        le=720,  # max 30 days
        description="Hours until invitation expires"
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional personal message to include in invitation"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newmember@example.com",
                "role": "member",
                "expires_in_hours": 72,
                "message": "Join our team workspace!"
            }
        }
    }


class InvitationBulkCreate(BaseModel):
    """Request model for creating multiple invitations."""
    emails: List[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of email addresses to invite"
    )
    role: WorkspaceRole = Field(
        default=WorkspaceRole.MEMBER,
        description="Role to assign to all invitees"
    )
    expires_in_hours: int = Field(
        default=168,
        ge=1,
        le=720,
        description="Hours until invitations expire"
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional message for all invitations"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "emails": ["user1@example.com", "user2@example.com"],
                "role": "member",
                "expires_in_hours": 72
            }
        }
    }


class InvitationAccept(BaseModel):
    """Request model for accepting an invitation (can include token in body)."""
    token: Optional[str] = Field(
        None,
        description="Invitation token (alternative to URL parameter)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "inv_abc123xyz789"
            }
        }
    }


# === Response Models ===

class InvitationInfo(BaseModel):
    """Full invitation information."""
    id: str = Field(..., description="Invitation ID")
    workspace_id: str = Field(..., description="Target workspace ID")
    workspace_name: str = Field(..., description="Target workspace name")
    email: str = Field(..., description="Invitee email address")
    role: WorkspaceRole = Field(..., description="Role to be assigned")
    status: InvitationStatus = Field(..., description="Current invitation status")
    token: str = Field(..., description="Unique invitation token")
    invited_by_id: str = Field(..., description="User ID of inviter")
    invited_by_name: Optional[str] = Field(None, description="Display name of inviter")
    message: Optional[str] = Field(None, description="Personal message from inviter")
    created_at: str = Field(..., description="When invitation was created")
    expires_at: str = Field(..., description="When invitation expires")
    accepted_at: Optional[str] = Field(None, description="When invitation was accepted")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "inv_abc123",
                "workspace_id": "ws_xyz789",
                "workspace_name": "Engineering Team",
                "email": "newmember@example.com",
                "role": "member",
                "status": "pending",
                "token": "inv_abc123xyz789secret",
                "invited_by_id": "user_123",
                "invited_by_name": "John Doe",
                "message": "Join our team!",
                "created_at": "2025-12-27T10:00:00-08:00",
                "expires_at": "2025-12-30T10:00:00-08:00",
                "accepted_at": None
            }
        }
    }


class InvitationSummary(BaseModel):
    """Summary for invitation listing (excludes token for security)."""
    id: str = Field(..., description="Invitation ID")
    email: str = Field(..., description="Invitee email")
    role: WorkspaceRole = Field(..., description="Role to be assigned")
    status: InvitationStatus = Field(..., description="Current status")
    created_at: str = Field(..., description="When created")
    expires_at: str = Field(..., description="When expires")
    accepted_at: Optional[str] = Field(None, description="When accepted")


class InvitationListResponse(BaseModel):
    """Response for listing workspace invitations."""
    invitations: List[InvitationSummary] = Field(..., description="List of invitations")
    total: int = Field(..., description="Total count")
    pending_count: int = Field(default=0, description="Count of pending invitations")
    workspace_id: str = Field(..., description="Workspace ID")


class InvitationCreateResponse(BaseModel):
    """Response after creating an invitation."""
    invitation: InvitationInfo = Field(..., description="Created invitation")
    invite_url: str = Field(..., description="URL to send to invitee")
    message: str = Field(..., description="Confirmation message")


class InvitationBulkCreateResponse(BaseModel):
    """Response after creating multiple invitations."""
    created: List[InvitationInfo] = Field(..., description="Successfully created invitations")
    failed: List[dict] = Field(
        default_factory=list,
        description="Emails that failed (with reason)"
    )
    total_created: int = Field(..., description="Count of created invitations")
    total_failed: int = Field(..., description="Count of failed invitations")


class InvitationAcceptResponse(BaseModel):
    """Response after accepting an invitation."""
    workspace_id: str = Field(..., description="Workspace joined")
    workspace_name: str = Field(..., description="Name of workspace")
    role: WorkspaceRole = Field(..., description="Assigned role")
    message: str = Field(..., description="Welcome message")


class InvitationValidateResponse(BaseModel):
    """Response when validating an invitation token (for UI preview)."""
    valid: bool = Field(..., description="Whether token is valid")
    workspace_name: Optional[str] = Field(None, description="Workspace name if valid")
    invited_by: Optional[str] = Field(None, description="Who sent the invitation")
    role: Optional[WorkspaceRole] = Field(None, description="Role to be assigned")
    expires_at: Optional[str] = Field(None, description="Expiration time")
    error: Optional[str] = Field(None, description="Error message if invalid")


class InvitationCancelResponse(BaseModel):
    """Response after cancelling an invitation."""
    invitation_id: str = Field(..., description="Cancelled invitation ID")
    email: str = Field(..., description="Email of cancelled invitation")
    message: str = Field(..., description="Confirmation message")


class InvitationResendResponse(BaseModel):
    """Response after resending an invitation."""
    invitation: InvitationInfo = Field(..., description="Updated invitation")
    new_expires_at: str = Field(..., description="New expiration time")
    message: str = Field(..., description="Confirmation message")
