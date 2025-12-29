"""
Webhooks Router

Handles incoming webhooks from external services.
No authentication required - uses signature verification instead.

Supported webhooks:
- ClickUp: Task comments, task updates
- Gmail: Push notifications via Pub/Sub
- Stripe: Payment events with signature verification
- Energy: Chrome extension and SMS tracking
"""
import hmac
import hashlib
import base64
import json
import os
import logging
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import ValidationError
from supabase import create_client, Client

from models.webhooks import (
    ClickUpWebhookPayload,
    WebhookResponse,
    GmailPushPayload,
    GmailPushData,
    StripeWebhookPayload,
    EnergyWebhookPayload,
)
from services.ai_responder import handle_comment_event


router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)

# Pacific timezone for all time operations
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for database operations."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if url and key:
        return create_client(url, key)
    return None


# === Signature Verification Functions ===

def verify_clickup_signature(body: bytes, signature: str) -> bool:
    """Verify ClickUp webhook signature using HMAC-SHA256.

    Args:
        body: Raw request body as bytes
        signature: X-Signature header value from ClickUp

    Returns:
        True if signature is valid
    """
    from config import get_settings
    settings = get_settings()
    secret = settings.clickup_webhook_secret or ""

    if not secret:
        # During development/testing, allow unsigned requests
        logger.warning("CLICKUP_WEBHOOK_SECRET not set - skipping signature verification")
        return True

    expected = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def verify_stripe_signature(body: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature using their scheme.

    Stripe uses a custom signature format: t=timestamp,v1=signature
    The signature is HMAC-SHA256(timestamp.payload, secret)

    Args:
        body: Raw request body as bytes
        signature: Stripe-Signature header value

    Returns:
        True if signature is valid
    """
    secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

    if not secret:
        logger.warning("STRIPE_WEBHOOK_SECRET not set - skipping signature verification")
        return True

    try:
        # Parse Stripe signature header: t=1234567890,v1=abc123...
        elements = dict(item.split("=", 1) for item in signature.split(","))
        timestamp = elements.get("t", "")
        sig = elements.get("v1", "")

        if not timestamp or not sig:
            logger.warning("Invalid Stripe signature format")
            return False

        # Create signed payload string: timestamp.body
        signed_payload = f"{timestamp}.{body.decode('utf-8')}"

        # Compute expected signature
        expected = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, sig)

    except Exception as e:
        logger.error(f"Error verifying Stripe signature: {e}")
        return False


def verify_energy_secret(secret: str) -> bool:
    """Verify energy webhook shared secret.

    Args:
        secret: Shared secret from webhook payload

    Returns:
        True if secret matches
    """
    expected_secret = os.getenv('ENERGY_WEBHOOK_SECRET', '')

    if not expected_secret:
        logger.warning("ENERGY_WEBHOOK_SECRET not set - skipping verification")
        return True

    return hmac.compare_digest(expected_secret, secret)


# === ClickUp Webhook ===

async def process_comment_webhook(payload: ClickUpWebhookPayload) -> None:
    """Process a taskCommentPosted webhook event.

    Runs in background to return 200 quickly to ClickUp.
    """
    import sys
    print(f"[WEBHOOK] Processing comment webhook for task {payload.task_id}", file=sys.stderr, flush=True)
    print(f"[WEBHOOK] History items count: {len(payload.history_items)}", file=sys.stderr, flush=True)
    print(f"[WEBHOOK] History items: {payload.history_items}", file=sys.stderr, flush=True)

    try:
        for history_item in payload.history_items:
            # history_items is now a list of dicts
            field = history_item.get("field", "")
            print(f"[WEBHOOK] History item field: {field}", file=sys.stderr, flush=True)

            if field != "comment":
                continue

            comment = history_item.get("comment", {})
            if not comment:
                print("[WEBHOOK] No comment object in history item", file=sys.stderr, flush=True)
                continue

            # Extract comment details - ClickUp uses various formats:
            # - text_content: direct text content (most common in taskCommentPosted)
            # - comment: array of {text: "..."} objects
            # - comment_text: older format
            comment_text = (
                comment.get("text_content", "") or
                comment.get("comment_text", "")
            )
            print(f"[WEBHOOK] Got text_content: {comment_text[:50] if comment_text else 'None'}", file=sys.stderr, flush=True)

            # Handle nested comment array format: {"comment": [{"text": "..."}]}
            if not comment_text:
                nested_comment = comment.get("comment", [])
                if isinstance(nested_comment, list) and nested_comment:
                    comment_text = nested_comment[0].get("text", "")

            user = comment.get("user", {})
            user_name = user.get("username", "Unknown")
            user_id = user.get("id", 0)

            if not comment_text:
                print(f"[WEBHOOK] No comment text found in payload: {list(comment.keys())}", file=sys.stderr, flush=True)
                continue

            print(f"[WEBHOOK] Processing comment from {user_name} (ID: {user_id}): {comment_text[:50]}...", file=sys.stderr, flush=True)

            try:
                result = await handle_comment_event(
                    task_id=payload.task_id,
                    user_comment=comment_text,
                    user_name=user_name,
                    user_id=user_id,
                )
                print(f"[WEBHOOK] Comment handling result: {result}", file=sys.stderr, flush=True)
            except Exception as inner_e:
                print(f"[WEBHOOK] Error in handle_comment_event: {inner_e}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)

    except Exception as e:
        print(f"[WEBHOOK] Error processing webhook: {e}")
        import traceback
        traceback.print_exc()


@router.post("/clickup", response_model=WebhookResponse)
async def clickup_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> WebhookResponse:
    """Receive ClickUp webhook events.

    Handles taskCommentPosted events to trigger AI responses.
    Uses signature verification instead of auth tokens.

    **No authentication required** - signature verification provides security.
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify signature
    signature = request.headers.get("X-Signature", "")
    if not verify_clickup_signature(body, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    try:
        payload_dict = await request.json()
        payload = ClickUpWebhookPayload(**payload_dict)
    except ValidationError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to parse webhook: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse payload")

    logger.info(f"Received ClickUp webhook: event={payload.event}, task_id={payload.task_id}")

    # Handle different event types
    if payload.event == "taskCommentPosted":
        # Process in background to return 200 quickly
        background_tasks.add_task(process_comment_webhook, payload)
        return WebhookResponse(
            success=True,
            message="Comment event queued for processing",
            event_id=payload.webhook_id,
        )

    # Acknowledge other events without processing
    return WebhookResponse(
        success=True,
        message=f"Event {payload.event} received but not processed",
        event_id=payload.webhook_id,
    )


# === Gmail Push Notification Webhook ===

async def process_gmail_notification(email_address: str, history_id: int) -> None:
    """Process Gmail push notification in background.

    Triggers email sync for the affected mailbox.
    """
    logger.info(f"[GMAIL] Processing notification for {email_address}, history_id={history_id}")
    # TODO: Trigger email sync via gmail_integration service
    # This would call the gmail sync service to fetch new messages


@router.post("/gmail", response_model=WebhookResponse)
async def gmail_push_notification(
    request: Request,
    background_tasks: BackgroundTasks,
) -> WebhookResponse:
    """Receive Gmail push notifications via Google Cloud Pub/Sub.

    Gmail uses Pub/Sub for push notifications about mailbox changes.
    The payload contains a base64-encoded message with email and history ID.

    **No authentication required** - Pub/Sub handles verification.

    **Returns 200 immediately** to acknowledge receipt.
    Processing happens in background to avoid timeout.
    """
    try:
        payload_dict = await request.json()
        payload = GmailPushPayload(**payload_dict)
    except ValidationError as e:
        logger.error(f"Invalid Gmail push payload: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to parse Gmail push: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse payload")

    # Decode base64 message data
    try:
        decoded_data = base64.b64decode(payload.message.data).decode('utf-8')
        data_dict = json.loads(decoded_data)
        push_data = GmailPushData(**data_dict)
    except Exception as e:
        logger.error(f"Failed to decode Gmail push data: {e}")
        raise HTTPException(status_code=400, detail="Failed to decode message data")

    logger.info(f"Received Gmail push: email={push_data.email_address}, history_id={push_data.history_id}")

    # Process in background
    background_tasks.add_task(
        process_gmail_notification,
        push_data.email_address,
        push_data.history_id
    )

    return WebhookResponse(
        success=True,
        message="Gmail notification received",
        event_id=payload.message.message_id,
    )


# === Stripe Webhook ===

async def process_stripe_event(payload: StripeWebhookPayload) -> None:
    """Process Stripe webhook event in background.

    Handles various Stripe events like checkout completion, subscription updates.
    """
    logger.info(f"[STRIPE] Processing event: {payload.type}, id={payload.id}")

    event_type = payload.type
    data = payload.data.object

    # Handle specific event types
    if event_type == "checkout.session.completed":
        logger.info(f"[STRIPE] Checkout completed: {data.get('id')}")
        # TODO: Provision subscription, update user tier

    elif event_type == "customer.subscription.updated":
        logger.info(f"[STRIPE] Subscription updated: {data.get('id')}")
        # TODO: Update subscription status in database

    elif event_type == "customer.subscription.deleted":
        logger.info(f"[STRIPE] Subscription cancelled: {data.get('id')}")
        # TODO: Handle subscription cancellation

    elif event_type == "invoice.payment_succeeded":
        logger.info(f"[STRIPE] Payment succeeded: {data.get('id')}")
        # TODO: Record payment, extend subscription

    elif event_type == "invoice.payment_failed":
        logger.warning(f"[STRIPE] Payment failed: {data.get('id')}")
        # TODO: Notify user, retry logic

    else:
        logger.info(f"[STRIPE] Unhandled event type: {event_type}")


@router.post("/stripe", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> WebhookResponse:
    """Receive Stripe webhook events.

    Handles payment events like checkout completion, subscription updates.
    Uses Stripe signature verification for security.

    **No authentication required** - signature verification provides security.

    **Signature Format:**
    Stripe-Signature: t=timestamp,v1=signature

    **Returns 200 immediately** to acknowledge receipt.
    Processing happens in background to avoid timeout.
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify Stripe signature
    signature = request.headers.get("Stripe-Signature", "")
    if not verify_stripe_signature(body, signature):
        logger.warning("Invalid Stripe webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    try:
        payload_dict = await request.json()
        payload = StripeWebhookPayload(**payload_dict)
    except ValidationError as e:
        logger.error(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to parse Stripe webhook: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse payload")

    logger.info(f"Received Stripe webhook: type={payload.type}, id={payload.id}")

    # Process in background
    background_tasks.add_task(process_stripe_event, payload)

    return WebhookResponse(
        success=True,
        message=f"Stripe event {payload.type} received",
        event_id=payload.id,
    )


# === Energy Tracking Webhook ===

@router.post("/energy", response_model=WebhookResponse)
async def energy_webhook(
    request: Request,
) -> WebhookResponse:
    """Receive energy tracking data from Chrome extension or SMS.

    Stores energy level and focus quality directly to database.
    Uses shared secret for validation instead of auth tokens.

    **No authentication required** - shared secret provides security.

    **Request Body:**
    - energy_level: 1-10 energy rating
    - focus_quality: deep, shallow, or distracted
    - source: webhook, chrome_extension, sms
    - secret: Shared secret for validation
    - user_id: Optional user identifier
    - tenant_id: Optional tenant identifier
    - notes: Optional contextual notes
    """
    try:
        payload_dict = await request.json()
        payload = EnergyWebhookPayload(**payload_dict)
    except ValidationError as e:
        logger.error(f"Invalid energy webhook payload: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to parse energy webhook: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse payload")

    # Verify shared secret
    if not verify_energy_secret(payload.secret):
        logger.warning("Invalid energy webhook secret")
        raise HTTPException(status_code=401, detail="Invalid secret")

    # Store to database
    try:
        client = get_supabase_client()
        if not client:
            logger.error("Database connection not available")
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Use provided timestamp or current time
        if payload.timestamp:
            try:
                timestamp = datetime.fromisoformat(payload.timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now(PACIFIC)
        else:
            timestamp = datetime.now(PACIFIC)

        # Determine user and tenant IDs
        user_id = payload.user_id or "webhook_user"
        tenant_id = payload.tenant_id or "default"

        # Insert tracking entry
        result = client.table('energy_tracking').insert({
            'tenant_id': tenant_id,
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'energy_level': payload.energy_level,
            'focus_quality': payload.focus_quality,
            'source': payload.source,
            'notes': payload.notes,
        }).execute()

        if result.data:
            entry_id = result.data[0].get('id', 'unknown')
            logger.info(f"Energy recorded: id={entry_id}, level={payload.energy_level}, quality={payload.focus_quality}")

            return WebhookResponse(
                success=True,
                message=f"Energy level {payload.energy_level} recorded",
                event_id=entry_id,
            )
        else:
            logger.error("Failed to insert energy tracking entry")
            raise HTTPException(status_code=500, detail="Failed to record energy")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing energy data: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# === Health Check ===

@router.get("/health")
async def webhook_health() -> dict:
    """Health check for webhook endpoints.

    Shows configuration status for all webhook handlers.
    """
    from config import get_settings
    settings = get_settings()

    return {
        "status": "healthy",
        "handlers": {
            "clickup": {
                "enabled": True,
                "secret_configured": bool(settings.clickup_webhook_secret),
            },
            "gmail": {
                "enabled": True,
                "note": "Uses Pub/Sub for verification",
            },
            "stripe": {
                "enabled": True,
                "secret_configured": bool(os.getenv('STRIPE_WEBHOOK_SECRET')),
            },
            "energy": {
                "enabled": True,
                "secret_configured": bool(os.getenv('ENERGY_WEBHOOK_SECRET')),
                "database_available": bool(get_supabase_client()),
            },
        },
    }
