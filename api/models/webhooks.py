"""
Webhook Models

Pydantic models for webhook event payloads from external services.
Note: ClickUp webhook payloads use loose schemas, so we use Optional fields liberally.
"""
from typing import Optional, Any, List
from pydantic import BaseModel, Field


# === Gmail Push Notification Models ===

class GmailPushMessage(BaseModel):
    """Gmail Pub/Sub push notification message data."""
    data: str = Field(..., description="Base64-encoded message data")
    message_id: str = Field(..., alias="messageId", description="Pub/Sub message ID")
    publish_time: Optional[str] = Field(None, alias="publishTime", description="Publish timestamp")

    class Config:
        populate_by_name = True


class GmailPushPayload(BaseModel):
    """Gmail Pub/Sub push notification payload.

    Gmail uses Google Cloud Pub/Sub for push notifications.
    The payload contains a message with base64-encoded data.
    """
    message: GmailPushMessage = Field(..., description="Push message")
    subscription: str = Field(..., description="Pub/Sub subscription name")


class GmailPushData(BaseModel):
    """Decoded Gmail push notification data.

    The actual notification data after base64 decoding.
    """
    email_address: str = Field(..., alias="emailAddress", description="Gmail address")
    history_id: int = Field(..., alias="historyId", description="Gmail history ID")

    class Config:
        populate_by_name = True


# === Stripe Webhook Models ===

class StripeEventData(BaseModel):
    """Stripe event data object."""
    object: dict = Field(default_factory=dict, description="Event data object")
    previous_attributes: Optional[dict] = Field(None, description="Previous object state")


class StripeWebhookPayload(BaseModel):
    """Stripe webhook event payload.

    Stripe webhooks include event type and related data.
    Signature verification is done before parsing.
    """
    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type (e.g., checkout.session.completed)")
    api_version: Optional[str] = Field(None, description="Stripe API version")
    created: int = Field(..., description="Event creation timestamp")
    data: StripeEventData = Field(..., description="Event data")
    livemode: bool = Field(default=False, description="Live mode flag")

    class Config:
        extra = "allow"


# === Energy Tracking Webhook Models ===

class EnergyWebhookPayload(BaseModel):
    """Energy tracking webhook payload.

    Used by Chrome extension and SMS to record energy levels.
    No auth token required - uses shared secret for validation.
    """
    energy_level: int = Field(..., ge=1, le=10, description="Energy level 1-10")
    focus_quality: str = Field(..., pattern="^(deep|shallow|distracted)$", description="Focus quality")
    source: str = Field(default="webhook", description="Tracking source")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    current_task: Optional[str] = Field(None, max_length=200, description="Current task")
    user_id: Optional[str] = Field(None, description="User identifier (email)")
    tenant_id: Optional[str] = Field(None, description="Tenant identifier")
    timestamp: Optional[str] = Field(None, description="Recording timestamp (ISO format)")
    secret: str = Field(..., description="Shared secret for validation")


# === ClickUp Webhook Models ===

class ClickUpWebhookPayload(BaseModel):
    """ClickUp webhook event payload.

    Webhook events include:
    - taskCommentPosted: New comment on a task
    - taskCommentUpdated: Comment was edited
    - taskUpdated: Task was modified

    Note: Uses loose schema to handle ClickUp's varying payload formats.
    We parse the raw dict in the handler since ClickUp payloads vary significantly.
    """
    webhook_id: str
    event: str
    task_id: str
    history_items: list[dict] = []  # Keep as list of dicts for flexibility

    class Config:
        extra = "allow"


class WebhookResponse(BaseModel):
    """Standard response for webhook endpoints."""
    success: bool
    message: str
    event_id: Optional[str] = None
