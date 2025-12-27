"""
Workspace Invitations Router

Endpoints for managing workspace invitations.
Enables secure workspace access via unique invitation tokens.

Acceptance Criteria:
- Creates unique token per invitation
- Accept creates workspace membership
- Expired invitations return 410 Gone
"""
import os
import logging
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel

from models.response import APIResponse, ResponseMeta
from models.workspace import WorkspaceRole
from models.invitation import (
    InvitationCreate,
    InvitationBulkCreate,
    InvitationAccept,
    InvitationStatus,
    InvitationInfo,
    InvitationSummary,
    InvitationListResponse,
    InvitationCreateResponse,
    InvitationBulkCreateResponse,
    InvitationAcceptResponse,
    InvitationValidateResponse,
    InvitationCancelResponse,
    InvitationResendResponse,
)
from middleware.auth import get_current_user, get_optional_user, UserContext
from config import get_settings


router = APIRouter(prefix="/api/invitations", tags=["Invitations"])

logger = logging.getLogger("flourisha.api.invitations")
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Supabase Client ===

def get_supabase():
    """Get Supabase client for invitation operations."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured"
        )
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_service_key)


# === Helper Functions ===

def generate_invitation_id() -> str:
    """Generate a unique invitation ID."""
    return f"inv_{uuid.uuid4().hex[:16]}"


def generate_invitation_token() -> str:
    """Generate a secure, unique invitation token."""
    # Use URL-safe token: 32 bytes = 43 characters base64
    return secrets.token_urlsafe(32)


def now_pacific() -> datetime:
    """Get current time in Pacific timezone."""
    return datetime.now(PACIFIC)


def now_pacific_str() -> str:
    """Get current time in Pacific timezone as ISO string."""
    return now_pacific().isoformat()


async def get_workspace_by_id(workspace_id: str, supabase) -> Optional[dict]:
    """Get workspace by ID."""
    try:
        result = supabase.table("tenants").select("*").eq("tenant_id", workspace_id).single().execute()
        return result.data
    except Exception:
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


async def is_user_in_workspace(user_id: str, workspace_id: str, supabase) -> bool:
    """Check if a user is already a member of a workspace."""
    try:
        result = supabase.table("tenant_users").select("user_id").eq(
            "tenant_id", workspace_id
        ).eq("user_id", user_id).single().execute()
        return result.data is not None
    except Exception:
        return False


async def get_user_by_email(email: str, supabase) -> Optional[dict]:
    """Find a user by their email address."""
    try:
        result = supabase.table("users").select(
            "id, email, display_name"
        ).eq("email", email.lower()).single().execute()
        return result.data
    except Exception:
        return None


async def get_user_by_id(user_id: str, supabase) -> Optional[dict]:
    """Get user by their ID."""
    try:
        result = supabase.table("users").select(
            "id, email, display_name"
        ).eq("id", user_id).single().execute()
        return result.data
    except Exception:
        return None


async def get_invitation_by_token(token: str, supabase) -> Optional[dict]:
    """Get an invitation by its token."""
    try:
        result = supabase.table("workspace_invitations").select(
            "*, tenants(tenant_id, name)"
        ).eq("token", token).single().execute()
        return result.data
    except Exception:
        return None


async def get_invitation_by_id(invitation_id: str, supabase) -> Optional[dict]:
    """Get an invitation by its ID."""
    try:
        result = supabase.table("workspace_invitations").select(
            "*, tenants(tenant_id, name)"
        ).eq("id", invitation_id).single().execute()
        return result.data
    except Exception:
        return None


async def check_existing_pending_invitation(
    workspace_id: str, email: str, supabase
) -> Optional[dict]:
    """Check if there's already a pending invitation for this email."""
    try:
        result = supabase.table("workspace_invitations").select("*").eq(
            "workspace_id", workspace_id
        ).eq("email", email.lower()).eq("status", "pending").single().execute()
        return result.data
    except Exception:
        return None


def invitation_to_info(invitation: dict, workspace_name: str = None, inviter_name: str = None) -> InvitationInfo:
    """Convert database invitation record to InvitationInfo model."""
    tenant_data = invitation.get("tenants", {}) or {}
    ws_name = workspace_name or tenant_data.get("name", "Unknown")

    return InvitationInfo(
        id=invitation.get("id", ""),
        workspace_id=invitation.get("workspace_id", ""),
        workspace_name=ws_name,
        email=invitation.get("email", ""),
        role=WorkspaceRole(invitation.get("role", "member")),
        status=InvitationStatus(invitation.get("status", "pending")),
        token=invitation.get("token", ""),
        invited_by_id=invitation.get("invited_by", ""),
        invited_by_name=inviter_name or invitation.get("invited_by_name"),
        message=invitation.get("message"),
        created_at=invitation.get("created_at", ""),
        expires_at=invitation.get("expires_at", ""),
        accepted_at=invitation.get("accepted_at"),
    )


def invitation_to_summary(invitation: dict) -> InvitationSummary:
    """Convert database invitation record to InvitationSummary (no token)."""
    return InvitationSummary(
        id=invitation.get("id", ""),
        email=invitation.get("email", ""),
        role=WorkspaceRole(invitation.get("role", "member")),
        status=InvitationStatus(invitation.get("status", "pending")),
        created_at=invitation.get("created_at", ""),
        expires_at=invitation.get("expires_at", ""),
        accepted_at=invitation.get("accepted_at"),
    )


def get_invite_url(token: str) -> str:
    """Generate the invitation URL."""
    settings = get_settings()
    base_url = getattr(settings, 'frontend_url', None) or "https://app.flourisha.io"
    return f"{base_url}/invite/{token}"


def is_invitation_expired(expires_at: str) -> bool:
    """Check if an invitation has expired."""
    try:
        expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        # Convert to timezone-aware if naive
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=PACIFIC)
        return now_pacific() > expiry
    except Exception:
        return True


# === Endpoints ===

@router.get("/workspace/{workspace_id}", response_model=APIResponse[InvitationListResponse])
async def list_workspace_invitations(
    workspace_id: str,
    request: Request,
    status_filter: Optional[str] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvitationListResponse]:
    """
    List all invitations for a workspace.

    Only owners and admins can view invitations.
    Optionally filter by status (pending, accepted, expired, cancelled).
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify user has admin/owner access
        role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can view invitations"
            )

        # Build query
        query = supabase.table("workspace_invitations").select("*").eq(
            "workspace_id", workspace_id
        ).order("created_at", desc=True)

        if status_filter:
            query = query.eq("status", status_filter)

        result = query.execute()
        invitations_data = result.data or []

        # Convert to summaries
        invitations = [invitation_to_summary(inv) for inv in invitations_data]
        pending_count = sum(1 for inv in invitations if inv.status == InvitationStatus.PENDING)

        return APIResponse(
            success=True,
            data=InvitationListResponse(
                invitations=invitations,
                total=len(invitations),
                pending_count=pending_count,
                workspace_id=workspace_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing invitations for workspace {workspace_id}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/workspace/{workspace_id}", response_model=APIResponse[InvitationCreateResponse], status_code=status.HTTP_201_CREATED)
async def create_invitation(
    workspace_id: str,
    invitation_data: InvitationCreate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvitationCreateResponse]:
    """
    Create a new workspace invitation.

    Creates unique token per invitation.
    Only owners and admins can create invitations.
    Cannot invite someone already in the workspace.
    Cannot invite if pending invitation already exists (use resend instead).
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify user has admin/owner access
        requester_role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if requester_role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can create invitations"
            )

        # Verify workspace exists
        workspace = await get_workspace_by_id(workspace_id, supabase)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found"
            )

        # Normalize email
        email = invitation_data.email.lower()

        # Check if user with this email already in workspace
        existing_user = await get_user_by_email(email, supabase)
        if existing_user and await is_user_in_workspace(existing_user.get("id"), workspace_id, supabase):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{email}' is already a member of this workspace"
            )

        # Check for existing pending invitation
        existing_invitation = await check_existing_pending_invitation(workspace_id, email, supabase)
        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A pending invitation already exists for '{email}'. Use resend to update it."
            )

        # Validate role assignment
        if invitation_data.role == WorkspaceRole.OWNER and requester_role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can invite with owner role"
            )

        # Generate invitation
        invitation_id = generate_invitation_id()
        token = generate_invitation_token()
        now = now_pacific()
        expires_at = now + timedelta(hours=invitation_data.expires_in_hours)

        # Get inviter name
        inviter = await get_user_by_id(user.uid, supabase)
        inviter_name = inviter.get("display_name") if inviter else user.name

        # Create invitation record
        invitation_record = {
            "id": invitation_id,
            "workspace_id": workspace_id,
            "email": email,
            "role": invitation_data.role.value,
            "status": "pending",
            "token": token,
            "invited_by": user.uid,
            "invited_by_name": inviter_name,
            "message": invitation_data.message,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
        }

        supabase.table("workspace_invitations").insert(invitation_record).execute()

        workspace_name = workspace.get("name", "Unknown")
        invite_url = get_invite_url(token)

        logger.info(f"Created invitation {invitation_id} for {email} to workspace {workspace_id}")

        return APIResponse(
            success=True,
            data=InvitationCreateResponse(
                invitation=invitation_to_info(
                    invitation_record,
                    workspace_name=workspace_name,
                    inviter_name=inviter_name
                ),
                invite_url=invite_url,
                message=f"Invitation sent to {email}",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating invitation: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/workspace/{workspace_id}/bulk", response_model=APIResponse[InvitationBulkCreateResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_invitations(
    workspace_id: str,
    bulk_data: InvitationBulkCreate,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvitationBulkCreateResponse]:
    """
    Create multiple invitations at once.

    Creates unique token per invitation.
    Skips emails that are already members or have pending invitations.
    Returns both successful and failed invitations.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        # Verify user has admin/owner access
        requester_role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if requester_role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can create invitations"
            )

        # Verify workspace exists
        workspace = await get_workspace_by_id(workspace_id, supabase)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found"
            )

        # Validate role
        if bulk_data.role == WorkspaceRole.OWNER and requester_role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can invite with owner role"
            )

        workspace_name = workspace.get("name", "Unknown")
        inviter = await get_user_by_id(user.uid, supabase)
        inviter_name = inviter.get("display_name") if inviter else user.name
        now = now_pacific()
        expires_at = now + timedelta(hours=bulk_data.expires_in_hours)

        created = []
        failed = []

        for email in bulk_data.emails:
            email = email.lower()

            try:
                # Check if already a member
                existing_user = await get_user_by_email(email, supabase)
                if existing_user and await is_user_in_workspace(existing_user.get("id"), workspace_id, supabase):
                    failed.append({"email": email, "reason": "Already a member"})
                    continue

                # Check for existing pending invitation
                existing_invitation = await check_existing_pending_invitation(workspace_id, email, supabase)
                if existing_invitation:
                    failed.append({"email": email, "reason": "Pending invitation exists"})
                    continue

                # Create invitation
                invitation_id = generate_invitation_id()
                token = generate_invitation_token()

                invitation_record = {
                    "id": invitation_id,
                    "workspace_id": workspace_id,
                    "email": email,
                    "role": bulk_data.role.value,
                    "status": "pending",
                    "token": token,
                    "invited_by": user.uid,
                    "invited_by_name": inviter_name,
                    "message": bulk_data.message,
                    "created_at": now.isoformat(),
                    "expires_at": expires_at.isoformat(),
                }

                supabase.table("workspace_invitations").insert(invitation_record).execute()
                created.append(invitation_to_info(
                    invitation_record,
                    workspace_name=workspace_name,
                    inviter_name=inviter_name
                ))

            except Exception as e:
                failed.append({"email": email, "reason": str(e)})

        logger.info(f"Bulk invitation: created {len(created)}, failed {len(failed)} for workspace {workspace_id}")

        return APIResponse(
            success=True,
            data=InvitationBulkCreateResponse(
                created=created,
                failed=failed,
                total_created=len(created),
                total_failed=len(failed),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk invitations: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/validate/{token}", response_model=APIResponse[InvitationValidateResponse])
async def validate_invitation(
    token: str,
    request: Request,
    user: Optional[UserContext] = Depends(get_optional_user),
) -> APIResponse[InvitationValidateResponse]:
    """
    Validate an invitation token.

    Used by frontend to preview invitation details before accepting.
    Returns workspace name and inviter info if valid.
    Does not require authentication.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        invitation = await get_invitation_by_token(token, supabase)

        if not invitation:
            return APIResponse(
                success=True,
                data=InvitationValidateResponse(
                    valid=False,
                    error="Invitation not found",
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Check status
        if invitation.get("status") != "pending":
            status_msg = {
                "accepted": "This invitation has already been accepted",
                "expired": "This invitation has expired",
                "cancelled": "This invitation has been cancelled",
            }.get(invitation.get("status"), "Invitation is no longer valid")

            return APIResponse(
                success=True,
                data=InvitationValidateResponse(
                    valid=False,
                    error=status_msg,
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Check expiration
        if is_invitation_expired(invitation.get("expires_at", "")):
            # Update status to expired
            supabase.table("workspace_invitations").update({
                "status": "expired"
            }).eq("id", invitation.get("id")).execute()

            return APIResponse(
                success=True,
                data=InvitationValidateResponse(
                    valid=False,
                    error="This invitation has expired",
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Get workspace name
        tenant_data = invitation.get("tenants", {}) or {}
        workspace_name = tenant_data.get("name", "Unknown")

        return APIResponse(
            success=True,
            data=InvitationValidateResponse(
                valid=True,
                workspace_name=workspace_name,
                invited_by=invitation.get("invited_by_name"),
                role=WorkspaceRole(invitation.get("role", "member")),
                expires_at=invitation.get("expires_at"),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Error validating invitation: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/accept/{token}", response_model=APIResponse[InvitationAcceptResponse])
async def accept_invitation(
    token: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvitationAcceptResponse]:
    """
    Accept an invitation and join the workspace.

    Accept creates workspace membership.
    User must be authenticated.
    User email must match invitation email.
    Expired invitations return 410 Gone.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        invitation = await get_invitation_by_token(token, supabase)

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )

        # Check expiration FIRST - return 410 Gone for expired
        if is_invitation_expired(invitation.get("expires_at", "")):
            # Update status
            supabase.table("workspace_invitations").update({
                "status": "expired"
            }).eq("id", invitation.get("id")).execute()

            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This invitation has expired"
            )

        # Check status
        inv_status = invitation.get("status")
        if inv_status != "pending":
            status_code = status.HTTP_410_GONE if inv_status == "expired" else status.HTTP_409_CONFLICT
            status_msg = {
                "accepted": "This invitation has already been accepted",
                "expired": "This invitation has expired",
                "cancelled": "This invitation has been cancelled",
            }.get(inv_status, "Invitation is no longer valid")

            raise HTTPException(
                status_code=status_code,
                detail=status_msg
            )

        # Verify email matches
        invitation_email = invitation.get("email", "").lower()
        user_email = (user.email or "").lower()

        if invitation_email != user_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This invitation was sent to {invitation_email}. Please sign in with that email."
            )

        workspace_id = invitation.get("workspace_id")

        # Check if user is already a member
        if await is_user_in_workspace(user.uid, workspace_id, supabase):
            # Mark invitation as accepted anyway
            supabase.table("workspace_invitations").update({
                "status": "accepted",
                "accepted_at": now_pacific_str(),
            }).eq("id", invitation.get("id")).execute()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You are already a member of this workspace"
            )

        # Add user to workspace
        role = invitation.get("role", "member")
        now = now_pacific_str()

        supabase.table("tenant_users").insert({
            "tenant_id": workspace_id,
            "user_id": user.uid,
            "role": role,
            "groups": [],
            "created_at": now,
        }).execute()

        # Update invitation status
        supabase.table("workspace_invitations").update({
            "status": "accepted",
            "accepted_at": now,
        }).eq("id", invitation.get("id")).execute()

        # Get workspace name
        workspace = await get_workspace_by_id(workspace_id, supabase)
        workspace_name = workspace.get("name", "Unknown") if workspace else "Unknown"

        logger.info(f"User {user.uid} accepted invitation and joined workspace {workspace_id}")

        return APIResponse(
            success=True,
            data=InvitationAcceptResponse(
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                role=WorkspaceRole(role),
                message=f"Welcome to {workspace_name}!",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/{invitation_id}", response_model=APIResponse[InvitationCancelResponse])
async def cancel_invitation(
    invitation_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvitationCancelResponse]:
    """
    Cancel a pending invitation.

    Only owners and admins can cancel invitations.
    Cannot cancel already accepted invitations.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        invitation = await get_invitation_by_id(invitation_id, supabase)

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )

        workspace_id = invitation.get("workspace_id")

        # Verify user has admin/owner access
        role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can cancel invitations"
            )

        # Check status
        if invitation.get("status") == "accepted":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot cancel an already accepted invitation"
            )

        # Update status to cancelled
        supabase.table("workspace_invitations").update({
            "status": "cancelled",
        }).eq("id", invitation_id).execute()

        email = invitation.get("email", "")
        logger.info(f"Cancelled invitation {invitation_id} for {email}")

        return APIResponse(
            success=True,
            data=InvitationCancelResponse(
                invitation_id=invitation_id,
                email=email,
                message=f"Invitation to {email} has been cancelled",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling invitation: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/{invitation_id}/resend", response_model=APIResponse[InvitationResendResponse])
async def resend_invitation(
    invitation_id: str,
    request: Request,
    extends_hours: int = 72,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvitationResendResponse]:
    """
    Resend an invitation with a new expiration time.

    Generates a new token and extends expiration.
    Only works for pending invitations.
    Only owners and admins can resend.
    """
    supabase = get_supabase()
    meta_dict = request.state.get_meta()

    try:
        invitation = await get_invitation_by_id(invitation_id, supabase)

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )

        workspace_id = invitation.get("workspace_id")

        # Verify user has admin/owner access
        role = await get_user_role_in_workspace(user.uid, workspace_id, supabase)
        if role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can resend invitations"
            )

        # Can only resend pending or expired
        inv_status = invitation.get("status")
        if inv_status not in ("pending", "expired"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot resend invitation with status '{inv_status}'"
            )

        # Generate new token and expiration
        new_token = generate_invitation_token()
        now = now_pacific()
        new_expires_at = now + timedelta(hours=extends_hours)

        # Update invitation
        supabase.table("workspace_invitations").update({
            "token": new_token,
            "status": "pending",
            "expires_at": new_expires_at.isoformat(),
        }).eq("id", invitation_id).execute()

        # Fetch updated invitation
        updated = await get_invitation_by_id(invitation_id, supabase)

        # Get workspace name
        workspace = await get_workspace_by_id(workspace_id, supabase)
        workspace_name = workspace.get("name", "Unknown") if workspace else "Unknown"

        logger.info(f"Resent invitation {invitation_id}")

        return APIResponse(
            success=True,
            data=InvitationResendResponse(
                invitation=invitation_to_info(updated, workspace_name=workspace_name),
                new_expires_at=new_expires_at.isoformat(),
                message=f"Invitation resent to {invitation.get('email')}",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending invitation: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
