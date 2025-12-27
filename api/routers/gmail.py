"""
Gmail Integration Router

Endpoints for Gmail OAuth authentication and email sync management.
Implements web-based OAuth flow for Gmail access.
"""
import os
import sys
import pickle
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext

# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/gmail", tags=["Gmail Integration"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")

# Gmail OAuth configuration
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


# === Request/Response Models ===

class OAuthState(BaseModel):
    """OAuth state tracking."""
    state: str = Field(..., description="OAuth state token")
    auth_url: str = Field(..., description="Google consent URL")
    expires_at: str = Field(..., description="State expiration time")


class OAuthCallbackResponse(BaseModel):
    """Response after OAuth callback."""
    success: bool = Field(..., description="Whether authentication succeeded")
    email: Optional[str] = Field(None, description="Authenticated email address")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")


class GmailLabel(BaseModel):
    """Gmail label information."""
    id: str = Field(..., description="Label ID")
    name: str = Field(..., description="Label name")
    type: str = Field(default="user", description="Label type")
    message_count: Optional[int] = Field(None, description="Number of messages")
    unread_count: Optional[int] = Field(None, description="Number of unread messages")


class SyncConfig(BaseModel):
    """Gmail sync configuration."""
    labels: List[str] = Field(default_factory=list, description="Labels to sync")
    include_attachments: bool = Field(default=True, description="Download attachments")
    max_messages: int = Field(default=100, description="Max messages per sync")
    since_days: int = Field(default=30, description="Sync messages from last N days")


class SyncStatus(BaseModel):
    """Gmail sync status."""
    is_authenticated: bool = Field(..., description="Whether authenticated")
    last_sync: Optional[str] = Field(None, description="Last sync timestamp")
    sync_labels: List[str] = Field(default_factory=list, description="Configured sync labels")
    total_synced: int = Field(default=0, description="Total messages synced")
    pending_sync: int = Field(default=0, description="Messages pending sync")


class EmailMessage(BaseModel):
    """Email message summary."""
    id: str = Field(..., description="Message ID")
    thread_id: str = Field(..., description="Thread ID")
    subject: Optional[str] = Field(None, description="Email subject")
    sender: Optional[str] = Field(None, description="Sender email")
    date: Optional[str] = Field(None, description="Date received")
    snippet: Optional[str] = Field(None, description="Message snippet")
    labels: List[str] = Field(default_factory=list, description="Applied labels")
    has_attachments: bool = Field(default=False, description="Has attachments")


class SyncLabelsRequest(BaseModel):
    """Request to update sync labels."""
    labels: List[str] = Field(..., description="Labels to sync (by name or ID)")


# === Helper Functions ===

def get_credentials_path() -> str:
    """Get path to Gmail credentials.json"""
    return os.getenv('GMAIL_CREDENTIALS_PATH', '/root/.config/gmail/credentials.json')


def get_token_path(user_id: str) -> str:
    """Get path to user's token file."""
    base_path = os.getenv('GMAIL_TOKEN_PATH', '/root/.config/gmail')
    return f"{base_path}/token_{user_id}.pickle"


def get_sync_config_path(user_id: str) -> str:
    """Get path to user's sync config."""
    base_path = os.getenv('GMAIL_TOKEN_PATH', '/root/.config/gmail')
    return f"{base_path}/sync_{user_id}.json"


async def get_gmail_credentials(user_id: str):
    """Get Gmail credentials for a user."""
    token_path = get_token_path(user_id)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as f:
            return pickle.load(f)
    return None


async def save_gmail_credentials(user_id: str, credentials):
    """Save Gmail credentials for a user."""
    token_path = get_token_path(user_id)
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, 'wb') as f:
        pickle.dump(credentials, f)


# === OAuth Endpoints ===

@router.get("/auth/start", response_model=APIResponse[OAuthState])
async def start_oauth(
    request: Request,
    redirect_uri: Optional[str] = Query(None, description="Custom redirect URI"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[OAuthState]:
    """
    Start Gmail OAuth flow.

    Returns the Google consent URL for the user to authorize access.
    The state token should be preserved for the callback.

    **Query Parameters:**
    - redirect_uri: Custom callback URL (defaults to /api/gmail/auth/callback)

    **Response:**
    - state: OAuth state token (for CSRF protection)
    - auth_url: URL to redirect user to for Google consent
    - expires_at: When the state expires

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    now = datetime.now(PACIFIC)

    try:
        from google_auth_oauthlib.flow import Flow

        credentials_path = get_credentials_path()

        if not os.path.exists(credentials_path):
            return APIResponse(
                success=False,
                data=None,
                error="Gmail credentials not configured. Please set up OAuth in Google Cloud Console.",
                meta=ResponseMeta(**meta_dict),
            )

        # Default redirect URI
        base_url = str(request.base_url).rstrip('/')
        callback_uri = redirect_uri or f"{base_url}/api/gmail/auth/callback"

        # Create OAuth flow
        flow = Flow.from_client_secrets_file(
            credentials_path,
            scopes=GMAIL_SCOPES,
            redirect_uri=callback_uri
        )

        # Generate authorization URL with state
        import secrets
        state = secrets.token_urlsafe(32)

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )

        # Store state for verification (in production, use Redis/DB)
        # For now, encode user_id in state
        state_with_user = f"{state}:{user.uid}"

        # Calculate expiration (10 minutes)
        from datetime import timedelta
        expires_at = now + timedelta(minutes=10)

        response_data = OAuthState(
            state=state_with_user,
            auth_url=auth_url,
            expires_at=expires_at.isoformat(),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"OAuth start failed: {str(e)}")
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to start OAuth: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/auth/callback")
async def oauth_callback(
    request: Request,
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="OAuth state token"),
    error: Optional[str] = Query(None, description="Error from Google"),
) -> RedirectResponse:
    """
    Handle Gmail OAuth callback.

    This endpoint receives the authorization code from Google after user consent.
    Exchanges the code for access/refresh tokens and stores them securely.

    **Query Parameters:**
    - code: Authorization code from Google
    - state: OAuth state token (for CSRF protection)
    - error: Error message if authorization failed

    **Returns:** Redirect to success or error page
    """
    if error:
        logger.error(f"OAuth callback error: {error}")
        return RedirectResponse(url=f"/auth/gmail/error?error={error}")

    try:
        from google_auth_oauthlib.flow import Flow

        # Extract user_id from state
        parts = state.rsplit(':', 1)
        if len(parts) != 2:
            return RedirectResponse(url="/auth/gmail/error?error=invalid_state")

        state_token, user_id = parts

        credentials_path = get_credentials_path()
        base_url = str(request.base_url).rstrip('/')
        callback_uri = f"{base_url}/api/gmail/auth/callback"

        # Exchange code for tokens
        flow = Flow.from_client_secrets_file(
            credentials_path,
            scopes=GMAIL_SCOPES,
            redirect_uri=callback_uri
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Save credentials for user
        await save_gmail_credentials(user_id, credentials)

        logger.info(f"Gmail OAuth completed for user {user_id}")
        return RedirectResponse(url="/auth/gmail/success")

    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        return RedirectResponse(url=f"/auth/gmail/error?error={str(e)}")


@router.get("/status", response_model=APIResponse[SyncStatus])
async def get_sync_status(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SyncStatus]:
    """
    Get Gmail sync status.

    Returns authentication status, last sync time, and configured labels.

    **Response:**
    - is_authenticated: Whether Gmail is connected
    - last_sync: When last sync occurred
    - sync_labels: Labels configured for sync
    - total_synced: Total messages synced
    - pending_sync: Messages waiting to be synced

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.tenant_id or user.uid

    try:
        credentials = await get_gmail_credentials(user_id)
        is_authenticated = credentials is not None and credentials.valid

        # Load sync config
        sync_labels = []
        last_sync = None
        total_synced = 0

        config_path = get_sync_config_path(user_id)
        if os.path.exists(config_path):
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
                sync_labels = config.get('labels', [])
                last_sync = config.get('last_sync')
                total_synced = config.get('total_synced', 0)

        response_data = SyncStatus(
            is_authenticated=is_authenticated,
            last_sync=last_sync,
            sync_labels=sync_labels,
            total_synced=total_synced,
            pending_sync=0,  # Would calculate from actual message count
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get sync status: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/labels", response_model=APIResponse[List[GmailLabel]])
async def list_labels(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[GmailLabel]]:
    """
    List Gmail labels.

    Returns all labels available in the user's Gmail account.
    Use these to configure which labels to sync.

    **Response:**
    - List of labels with IDs, names, and message counts

    **Requires:** Valid Firebase JWT, Gmail authentication
    """
    meta_dict = request.state.get_meta()
    user_id = user.tenant_id or user.uid

    try:
        credentials = await get_gmail_credentials(user_id)
        if not credentials:
            return APIResponse(
                success=False,
                data=None,
                error="Gmail not authenticated. Please complete OAuth first.",
                meta=ResponseMeta(**meta_dict),
            )

        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request as GRequest

        # Refresh credentials if needed
        if credentials.expired:
            credentials.refresh(GRequest())
            await save_gmail_credentials(user_id, credentials)

        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().labels().list(userId='me').execute()

        labels = []
        for label in results.get('labels', []):
            # Get label details for counts
            try:
                label_info = service.users().labels().get(
                    userId='me', id=label['id']
                ).execute()

                labels.append(GmailLabel(
                    id=label['id'],
                    name=label['name'],
                    type=label.get('type', 'user'),
                    message_count=label_info.get('messagesTotal'),
                    unread_count=label_info.get('messagesUnread'),
                ))
            except Exception:
                labels.append(GmailLabel(
                    id=label['id'],
                    name=label['name'],
                    type=label.get('type', 'user'),
                ))

        return APIResponse(
            success=True,
            data=labels,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to list labels: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/sync/labels", response_model=APIResponse[SyncStatus])
async def update_sync_labels(
    request: Request,
    labels_request: SyncLabelsRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SyncStatus]:
    """
    Update labels to sync.

    Configures which Gmail labels should be synced to the knowledge base.
    Only messages with these labels will be ingested.

    **Request Body:**
    - labels: List of label names or IDs to sync

    **Response:**
    - Updated sync status

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.tenant_id or user.uid
    now = datetime.now(PACIFIC)

    try:
        import json

        config_path = get_sync_config_path(user_id)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Load existing config or create new
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

        # Update labels
        config['labels'] = labels_request.labels
        config['updated_at'] = now.isoformat()

        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        response_data = SyncStatus(
            is_authenticated=await get_gmail_credentials(user_id) is not None,
            last_sync=config.get('last_sync'),
            sync_labels=labels_request.labels,
            total_synced=config.get('total_synced', 0),
            pending_sync=0,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to update sync labels: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/sync/run", response_model=APIResponse[dict])
async def run_sync(
    request: Request,
    max_messages: int = Query(100, description="Maximum messages to sync"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Run Gmail sync.

    Syncs messages from configured labels to the knowledge base.
    Messages are processed and ingested for search.

    **Query Parameters:**
    - max_messages: Maximum number of messages to sync

    **Response:**
    - synced: Number of messages synced
    - skipped: Number of messages skipped
    - errors: Number of errors
    - duration_ms: Sync duration

    **Requires:** Valid Firebase JWT, Gmail authentication
    """
    meta_dict = request.state.get_meta()
    user_id = user.tenant_id or user.uid
    now = datetime.now(PACIFIC)
    start_time = datetime.now()

    try:
        credentials = await get_gmail_credentials(user_id)
        if not credentials:
            return APIResponse(
                success=False,
                data=None,
                error="Gmail not authenticated. Please complete OAuth first.",
                meta=ResponseMeta(**meta_dict),
            )

        # Load sync config
        import json
        config_path = get_sync_config_path(user_id)
        sync_labels = []
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                sync_labels = config.get('labels', [])

        if not sync_labels:
            return APIResponse(
                success=False,
                data=None,
                error="No labels configured for sync. Use PUT /api/gmail/sync/labels first.",
                meta=ResponseMeta(**meta_dict),
            )

        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request as GRequest

        # Refresh credentials if needed
        if credentials.expired:
            credentials.refresh(GRequest())
            await save_gmail_credentials(user_id, credentials)

        service = build('gmail', 'v1', credentials=credentials)

        synced = 0
        skipped = 0
        errors = 0

        for label in sync_labels:
            try:
                # Get messages with this label
                results = service.users().messages().list(
                    userId='me',
                    labelIds=[label] if label.startswith('Label_') else None,
                    q=f"label:{label}" if not label.startswith('Label_') else None,
                    maxResults=max_messages
                ).execute()

                messages = results.get('messages', [])

                for msg_ref in messages:
                    try:
                        # Get full message
                        msg = service.users().messages().get(
                            userId='me',
                            id=msg_ref['id'],
                            format='full'
                        ).execute()

                        # Here you would ingest the message to knowledge base
                        # For now, just count it
                        synced += 1

                    except Exception as e:
                        logger.error(f"Error syncing message {msg_ref['id']}: {e}")
                        errors += 1

            except Exception as e:
                logger.error(f"Error syncing label {label}: {e}")
                errors += 1

        # Update sync config
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

        config['last_sync'] = now.isoformat()
        config['total_synced'] = config.get('total_synced', 0) + synced

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        return APIResponse(
            success=True,
            data={
                "synced": synced,
                "skipped": skipped,
                "errors": errors,
                "duration_ms": round(duration_ms, 2),
            },
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Sync failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/messages", response_model=APIResponse[List[EmailMessage]])
async def list_messages(
    request: Request,
    label: str = Query("INBOX", description="Label to list messages from"),
    query: str = Query("", description="Search query"),
    max_results: int = Query(20, description="Maximum results"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[EmailMessage]]:
    """
    List Gmail messages.

    Returns messages from the specified label or matching the search query.

    **Query Parameters:**
    - label: Gmail label (default: INBOX)
    - query: Search query (Gmail search syntax)
    - max_results: Maximum messages to return

    **Response:**
    - List of email message summaries

    **Requires:** Valid Firebase JWT, Gmail authentication
    """
    meta_dict = request.state.get_meta()
    user_id = user.tenant_id or user.uid

    try:
        credentials = await get_gmail_credentials(user_id)
        if not credentials:
            return APIResponse(
                success=False,
                data=None,
                error="Gmail not authenticated. Please complete OAuth first.",
                meta=ResponseMeta(**meta_dict),
            )

        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request as GRequest

        # Refresh credentials if needed
        if credentials.expired:
            credentials.refresh(GRequest())
            await save_gmail_credentials(user_id, credentials)

        service = build('gmail', 'v1', credentials=credentials)

        # Build query
        full_query = query
        if label and label != "INBOX":
            full_query = f"label:{label} {query}".strip()

        results = service.users().messages().list(
            userId='me',
            q=full_query,
            maxResults=max_results,
            labelIds=['INBOX'] if label == "INBOX" else None,
        ).execute()

        messages = []
        for msg_ref in results.get('messages', []):
            try:
                msg = service.users().messages().get(
                    userId='me',
                    id=msg_ref['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}

                # Check for attachments
                has_attachments = False
                payload = msg.get('payload', {})
                if 'parts' in payload:
                    has_attachments = any(
                        part.get('filename') for part in payload['parts']
                    )

                messages.append(EmailMessage(
                    id=msg['id'],
                    thread_id=msg['threadId'],
                    subject=headers.get('Subject'),
                    sender=headers.get('From'),
                    date=headers.get('Date'),
                    snippet=msg.get('snippet'),
                    labels=msg.get('labelIds', []),
                    has_attachments=has_attachments,
                ))
            except Exception as e:
                logger.error(f"Error fetching message {msg_ref['id']}: {e}")

        return APIResponse(
            success=True,
            data=messages,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to list messages: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/auth", response_model=APIResponse[dict])
async def revoke_auth(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Revoke Gmail authentication.

    Removes stored tokens and disconnects Gmail integration.

    **Response:**
    - revoked: Whether revocation succeeded

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.tenant_id or user.uid

    try:
        token_path = get_token_path(user_id)
        if os.path.exists(token_path):
            os.remove(token_path)

        return APIResponse(
            success=True,
            data={"revoked": True},
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to revoke auth: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
