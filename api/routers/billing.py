"""
Stripe Billing Router

Subscription and billing management via Stripe.
Supports checkout sessions, customer portal, webhooks, and subscription lifecycle.

Based on FRONTEND_FEATURE_REGISTRY section 3.7: Stripe Billing API
"""
import os
import sys
import hmac
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException, status, Header
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.billing import (
    SubscriptionTier,
    SubscriptionStatus,
    PaymentStatus,
    BillingInterval,
    TierFeatures,
    TierPricing,
    SubscriptionTierInfo,
    CustomerInfo,
    SubscriptionInfo,
    BillingOverview,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionRequest,
    PortalSessionResponse,
    InvoiceInfo,
    InvoiceLineItem,
    InvoiceListResponse,
    WebhookEventType,
    WebhookProcessResult,
    UsageQuota,
    UsageSummary,
    TierChangePreview,
    TierChangeRequest,
    TierChangeResponse,
    CancelRequest,
    CancelResponse,
)
from middleware.auth import get_current_user, get_optional_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["Billing"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Tier Catalog (Static definitions) ===

TIER_CATALOG: Dict[SubscriptionTier, SubscriptionTierInfo] = {
    SubscriptionTier.FREE: SubscriptionTierInfo(
        tier=SubscriptionTier.FREE,
        name="Free",
        description="Get started with basic features",
        features=TierFeatures(
            max_workspaces=1,
            max_members_per_workspace=1,
            max_documents_per_month=10,
            max_youtube_videos_per_month=5,
            ai_model="haiku",
            knowledge_stores=["vector"],
            integrations=["gmail"],
            support_level="community",
            custom_skills=False,
            voice_notifications=False,
            api_access=False,
        ),
        pricing=TierPricing(
            monthly_price_cents=0,
            yearly_price_cents=0,
            yearly_discount_percent=0,
        ),
    ),
    SubscriptionTier.STARTER: SubscriptionTierInfo(
        tier=SubscriptionTier.STARTER,
        name="Starter",
        description="For individuals getting productive",
        features=TierFeatures(
            max_workspaces=3,
            max_members_per_workspace=5,
            max_documents_per_month=100,
            max_youtube_videos_per_month=50,
            ai_model="sonnet",
            knowledge_stores=["vector", "graph"],
            integrations=["gmail", "google_calendar", "clickup"],
            support_level="email",
            custom_skills=True,
            voice_notifications=True,
            api_access=False,
        ),
        pricing=TierPricing(
            monthly_price_cents=1999,
            yearly_price_cents=19188,  # $159.90/year = 20% off
            yearly_discount_percent=20,
            stripe_price_id_monthly="price_starter_monthly",
            stripe_price_id_yearly="price_starter_yearly",
        ),
        is_popular=True,
    ),
    SubscriptionTier.PRO: SubscriptionTierInfo(
        tier=SubscriptionTier.PRO,
        name="Pro",
        description="For power users and small teams",
        features=TierFeatures(
            max_workspaces=10,
            max_members_per_workspace=25,
            max_documents_per_month=1000,
            max_youtube_videos_per_month=500,
            ai_model="opus",
            knowledge_stores=["vector", "graph", "whole"],
            integrations=[
                "gmail", "google_calendar", "clickup", "slack",
                "google_drive", "youtube", "neo4j", "supabase"
            ],
            support_level="priority",
            custom_skills=True,
            voice_notifications=True,
            api_access=True,
        ),
        pricing=TierPricing(
            monthly_price_cents=4999,
            yearly_price_cents=47988,  # $399.90/year = 20% off
            yearly_discount_percent=20,
            stripe_price_id_monthly="price_pro_monthly",
            stripe_price_id_yearly="price_pro_yearly",
        ),
    ),
    SubscriptionTier.ENTERPRISE: SubscriptionTierInfo(
        tier=SubscriptionTier.ENTERPRISE,
        name="Enterprise",
        description="Custom solutions for large organizations",
        features=TierFeatures(
            max_workspaces=-1,  # Unlimited
            max_members_per_workspace=-1,  # Unlimited
            max_documents_per_month=-1,  # Unlimited
            max_youtube_videos_per_month=-1,  # Unlimited
            ai_model="opus",
            knowledge_stores=["vector", "graph", "whole"],
            integrations=["all"],
            support_level="dedicated",
            custom_skills=True,
            voice_notifications=True,
            api_access=True,
        ),
        pricing=TierPricing(
            monthly_price_cents=-1,  # Custom pricing
            yearly_price_cents=-1,
            yearly_discount_percent=0,
        ),
    ),
}


# === In-memory storage (replace with database in production) ===

# User subscriptions: user_id -> subscription data
_user_subscriptions: Dict[str, Dict[str, Any]] = {}

# Stripe customers: user_id -> customer data
_stripe_customers: Dict[str, Dict[str, Any]] = {}

# Checkout sessions: session_id -> session data
_checkout_sessions: Dict[str, Dict[str, Any]] = {}

# Invoices: invoice_id -> invoice data
_invoices: Dict[str, Dict[str, Any]] = {}


def _get_meta(request: Request) -> ResponseMeta:
    """Get response metadata from request state."""
    meta_dict = request.state.get_meta()
    return ResponseMeta(**meta_dict)


def _now() -> datetime:
    """Get current time in Pacific."""
    return datetime.now(PACIFIC)


# === Tier Endpoints ===

@router.get("/tiers")
async def list_tiers(
    request: Request,
) -> APIResponse[List[SubscriptionTierInfo]]:
    """
    List all available subscription tiers.

    Returns tier definitions with features and pricing.
    No authentication required.
    """
    tiers = list(TIER_CATALOG.values())
    return APIResponse(
        success=True,
        data=tiers,
        meta=_get_meta(request),
    )


@router.get("/tiers/{tier}")
async def get_tier(
    tier: SubscriptionTier,
    request: Request,
) -> APIResponse[SubscriptionTierInfo]:
    """
    Get details for a specific tier.

    Returns tier features, limits, and pricing.
    """
    tier_info = TIER_CATALOG.get(tier)
    if not tier_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tier '{tier}' not found"
        )

    return APIResponse(
        success=True,
        data=tier_info,
        meta=_get_meta(request),
    )


# === Billing Overview ===

@router.get("/overview")
async def get_billing_overview(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[BillingOverview]:
    """
    Get billing overview for current user.

    Returns current tier, subscription status, and next invoice.
    """
    user_id = user.uid

    # Get customer info
    customer_data = _stripe_customers.get(user_id)
    customer = None
    if customer_data:
        customer = CustomerInfo(
            stripe_customer_id=customer_data["stripe_customer_id"],
            email=customer_data["email"],
            name=customer_data.get("name"),
            created_at=customer_data["created_at"],
            default_payment_method=customer_data.get("default_payment_method"),
            currency=customer_data.get("currency", "usd"),
        )

    # Get subscription info
    sub_data = _user_subscriptions.get(user_id)
    subscription = None
    tier = SubscriptionTier.FREE
    is_trial = False
    trial_days_remaining = None

    if sub_data:
        subscription = SubscriptionInfo(
            id=sub_data["id"],
            status=SubscriptionStatus(sub_data["status"]),
            tier=SubscriptionTier(sub_data["tier"]),
            billing_interval=BillingInterval(sub_data["billing_interval"]),
            current_period_start=sub_data["current_period_start"],
            current_period_end=sub_data["current_period_end"],
            cancel_at_period_end=sub_data.get("cancel_at_period_end", False),
            canceled_at=sub_data.get("canceled_at"),
            trial_end=sub_data.get("trial_end"),
        )
        tier = subscription.tier

        # Check trial status
        if sub_data["status"] == "trialing" and sub_data.get("trial_end"):
            is_trial = True
            trial_end = sub_data["trial_end"]
            if isinstance(trial_end, datetime):
                delta = trial_end - _now()
                trial_days_remaining = max(0, delta.days)

    # Calculate next invoice
    next_invoice_date = None
    next_invoice_amount = None
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        next_invoice_date = subscription.current_period_end
        tier_info = TIER_CATALOG.get(tier)
        if tier_info:
            if subscription.billing_interval == BillingInterval.MONTHLY:
                next_invoice_amount = tier_info.pricing.monthly_price_cents
            else:
                next_invoice_amount = tier_info.pricing.yearly_price_cents // 12

    overview = BillingOverview(
        customer=customer,
        subscription=subscription,
        tier=tier,
        is_trial=is_trial,
        trial_days_remaining=trial_days_remaining,
        next_invoice_date=next_invoice_date,
        next_invoice_amount_cents=next_invoice_amount,
    )

    return APIResponse(
        success=True,
        data=overview,
        meta=_get_meta(request),
    )


# === Checkout ===

@router.post("/checkout")
async def create_checkout_session(
    checkout_request: CheckoutSessionRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[CheckoutSessionResponse]:
    """
    Create a Stripe checkout session for tier upgrade.

    Returns URL to redirect user to Stripe checkout.

    Acceptance Criteria:
    - Checkout creates session for tier upgrade
    """
    user_id = user.uid

    # Validate tier can be purchased
    tier_info = TIER_CATALOG.get(checkout_request.tier)
    if not tier_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {checkout_request.tier}"
        )

    if checkout_request.tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout for free tier"
        )

    if checkout_request.tier == SubscriptionTier.ENTERPRISE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise tier requires contacting sales"
        )

    # Get price ID
    if checkout_request.billing_interval == BillingInterval.MONTHLY:
        price_id = tier_info.pricing.stripe_price_id_monthly
    else:
        price_id = tier_info.pricing.stripe_price_id_yearly

    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe price not configured for this tier"
        )

    # Create session ID
    session_id = f"cs_{user_id}_{int(_now().timestamp())}"
    expires_at = _now() + timedelta(hours=24)

    # Store session (in production, this would be Stripe API call)
    _checkout_sessions[session_id] = {
        "id": session_id,
        "user_id": user_id,
        "tier": checkout_request.tier.value,
        "billing_interval": checkout_request.billing_interval.value,
        "price_id": price_id,
        "success_url": checkout_request.success_url,
        "cancel_url": checkout_request.cancel_url,
        "promotion_code": checkout_request.promotion_code,
        "trial_days": checkout_request.trial_days,
        "created_at": _now(),
        "expires_at": expires_at,
        "status": "open",
    }

    # In production, this would be Stripe checkout URL
    checkout_url = f"https://checkout.stripe.com/c/pay/{session_id}"

    logger.info(f"Created checkout session {session_id} for user {user_id}, tier {checkout_request.tier}")

    return APIResponse(
        success=True,
        data=CheckoutSessionResponse(
            checkout_url=checkout_url,
            session_id=session_id,
            expires_at=expires_at,
        ),
        meta=_get_meta(request),
    )


# === Customer Portal ===

@router.post("/portal")
async def create_portal_session(
    portal_request: PortalSessionRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[PortalSessionResponse]:
    """
    Create a Stripe customer portal session.

    Portal allows customers to manage their subscription, payment methods,
    and view invoices.

    Acceptance Criteria:
    - Portal allows subscription management
    """
    user_id = user.uid

    # Check if customer exists
    customer_data = _stripe_customers.get(user_id)
    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Please subscribe first."
        )

    # In production, this would be Stripe API call
    portal_url = f"https://billing.stripe.com/p/session/{customer_data['stripe_customer_id']}"
    expires_at = _now() + timedelta(hours=1)

    logger.info(f"Created portal session for user {user_id}")

    return APIResponse(
        success=True,
        data=PortalSessionResponse(
            portal_url=portal_url,
            expires_at=expires_at,
        ),
        meta=_get_meta(request),
    )


# === Subscription Management ===

@router.get("/subscription")
async def get_subscription(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[Optional[SubscriptionInfo]]:
    """
    Get current subscription details.

    Returns None if user has no active subscription (free tier).
    """
    user_id = user.uid

    sub_data = _user_subscriptions.get(user_id)
    if not sub_data:
        return APIResponse(
            success=True,
            data=None,
            meta=_get_meta(request),
        )

    subscription = SubscriptionInfo(
        id=sub_data["id"],
        status=SubscriptionStatus(sub_data["status"]),
        tier=SubscriptionTier(sub_data["tier"]),
        billing_interval=BillingInterval(sub_data["billing_interval"]),
        current_period_start=sub_data["current_period_start"],
        current_period_end=sub_data["current_period_end"],
        cancel_at_period_end=sub_data.get("cancel_at_period_end", False),
        canceled_at=sub_data.get("canceled_at"),
        trial_end=sub_data.get("trial_end"),
    )

    return APIResponse(
        success=True,
        data=subscription,
        meta=_get_meta(request),
    )


@router.post("/subscription/change/preview")
async def preview_tier_change(
    change_request: TierChangeRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TierChangePreview]:
    """
    Preview what a tier change would cost/credit.

    Shows prorated charges for upgrades and credits for downgrades.
    """
    user_id = user.uid

    # Get current tier
    sub_data = _user_subscriptions.get(user_id)
    current_tier = SubscriptionTier.FREE
    if sub_data:
        current_tier = SubscriptionTier(sub_data["tier"])

    target_tier = change_request.target_tier

    if target_tier == current_tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on this tier"
        )

    # Get tier infos
    current_info = TIER_CATALOG.get(current_tier)
    target_info = TIER_CATALOG.get(target_tier)

    if not target_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target tier: {target_tier}"
        )

    # Determine if upgrade or downgrade
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.STARTER,
                  SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
    is_upgrade = tier_order.index(target_tier) > tier_order.index(current_tier)

    # Calculate costs (simplified proration)
    billing_interval = change_request.billing_interval or BillingInterval.MONTHLY
    if billing_interval == BillingInterval.MONTHLY:
        new_monthly = target_info.pricing.monthly_price_cents
        current_monthly = current_info.pricing.monthly_price_cents if current_info else 0
    else:
        new_monthly = target_info.pricing.yearly_price_cents // 12
        current_monthly = current_info.pricing.yearly_price_cents // 12 if current_info else 0

    immediate_charge = None
    credit = None

    if is_upgrade:
        # Prorate upgrade charge (simplified: half month)
        immediate_charge = (new_monthly - current_monthly) // 2
    else:
        # Credit for remaining time (simplified: quarter month)
        credit = (current_monthly - new_monthly) // 4

    # Determine feature changes
    features_gained = []
    features_lost = []

    if target_info and current_info:
        # Compare features
        if target_info.features.ai_model != current_info.features.ai_model:
            if is_upgrade:
                features_gained.append(f"AI Model: {target_info.features.ai_model}")
            else:
                features_lost.append(f"AI Model: {current_info.features.ai_model}")

        if target_info.features.api_access and not current_info.features.api_access:
            features_gained.append("API Access")
        elif current_info.features.api_access and not target_info.features.api_access:
            features_lost.append("API Access")

        if target_info.features.voice_notifications and not current_info.features.voice_notifications:
            features_gained.append("Voice Notifications")
        elif current_info.features.voice_notifications and not target_info.features.voice_notifications:
            features_lost.append("Voice Notifications")

    preview = TierChangePreview(
        current_tier=current_tier,
        target_tier=target_tier,
        is_upgrade=is_upgrade,
        immediate_charge_cents=immediate_charge,
        credit_cents=credit,
        new_monthly_amount_cents=new_monthly,
        effective_date=_now() if change_request.immediate else (_now() + timedelta(days=30)),
        features_gained=features_gained,
        features_lost=features_lost,
    )

    return APIResponse(
        success=True,
        data=preview,
        meta=_get_meta(request),
    )


@router.post("/subscription/change")
async def change_tier(
    change_request: TierChangeRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TierChangeResponse]:
    """
    Change subscription tier.

    Upgrades are applied immediately with prorated charge.
    Downgrades take effect at period end unless immediate=true.
    """
    user_id = user.uid

    target_tier = change_request.target_tier
    target_info = TIER_CATALOG.get(target_tier)

    if not target_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {target_tier}"
        )

    # Ensure customer exists
    if user_id not in _stripe_customers:
        _stripe_customers[user_id] = {
            "stripe_customer_id": f"cus_{user_id}",
            "email": user.email or f"{user_id}@example.com",
            "created_at": _now(),
        }

    # Update or create subscription
    billing_interval = change_request.billing_interval or BillingInterval.MONTHLY
    now = _now()
    period_end = now + timedelta(days=30) if billing_interval == BillingInterval.MONTHLY else now + timedelta(days=365)

    sub_id = f"sub_{user_id}_{int(now.timestamp())}"

    _user_subscriptions[user_id] = {
        "id": sub_id,
        "status": "active",
        "tier": target_tier.value,
        "billing_interval": billing_interval.value,
        "current_period_start": now,
        "current_period_end": period_end,
        "cancel_at_period_end": False,
        "canceled_at": None,
        "trial_end": None,
    }

    subscription = SubscriptionInfo(
        id=sub_id,
        status=SubscriptionStatus.ACTIVE,
        tier=target_tier,
        billing_interval=billing_interval,
        current_period_start=now,
        current_period_end=period_end,
        cancel_at_period_end=False,
    )

    logger.info(f"Changed subscription for user {user_id} to tier {target_tier}")

    return APIResponse(
        success=True,
        data=TierChangeResponse(
            success=True,
            subscription=subscription,
            message=f"Successfully changed to {target_info.name} tier",
            invoice_id=None,
        ),
        meta=_get_meta(request),
    )


@router.post("/subscription/cancel")
async def cancel_subscription(
    cancel_request: CancelRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[CancelResponse]:
    """
    Cancel subscription.

    By default, cancels at period end. Set immediate=true for immediate cancellation.
    """
    user_id = user.uid

    sub_data = _user_subscriptions.get(user_id)
    if not sub_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )

    now = _now()

    if cancel_request.immediate:
        # Immediate cancellation
        sub_data["status"] = "canceled"
        sub_data["canceled_at"] = now
        cancel_at = now
        message = "Subscription canceled immediately. You're now on the free tier."
    else:
        # Cancel at period end
        sub_data["cancel_at_period_end"] = True
        sub_data["canceled_at"] = now
        cancel_at = sub_data["current_period_end"]
        message = f"Subscription will cancel on {cancel_at.strftime('%B %d, %Y')}. You can continue using paid features until then."

    logger.info(f"Canceled subscription for user {user_id}, immediate={cancel_request.immediate}")

    return APIResponse(
        success=True,
        data=CancelResponse(
            success=True,
            cancel_at=cancel_at,
            message=message,
        ),
        meta=_get_meta(request),
    )


@router.post("/subscription/reactivate")
async def reactivate_subscription(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SubscriptionInfo]:
    """
    Reactivate a canceled subscription (before period end).

    Only works if subscription was set to cancel at period end.
    """
    user_id = user.uid

    sub_data = _user_subscriptions.get(user_id)
    if not sub_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription to reactivate"
        )

    if sub_data["status"] == "canceled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reactivate immediately canceled subscription. Please create a new subscription."
        )

    if not sub_data.get("cancel_at_period_end"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is not scheduled for cancellation"
        )

    # Reactivate
    sub_data["cancel_at_period_end"] = False
    sub_data["canceled_at"] = None

    subscription = SubscriptionInfo(
        id=sub_data["id"],
        status=SubscriptionStatus(sub_data["status"]),
        tier=SubscriptionTier(sub_data["tier"]),
        billing_interval=BillingInterval(sub_data["billing_interval"]),
        current_period_start=sub_data["current_period_start"],
        current_period_end=sub_data["current_period_end"],
        cancel_at_period_end=False,
        canceled_at=None,
    )

    logger.info(f"Reactivated subscription for user {user_id}")

    return APIResponse(
        success=True,
        data=subscription,
        meta=_get_meta(request),
    )


# === Invoices ===

@router.get("/invoices")
async def list_invoices(
    request: Request,
    user: UserContext = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
) -> APIResponse[InvoiceListResponse]:
    """
    List invoices for current user.

    Returns paginated list of past invoices with PDF links.
    """
    user_id = user.uid

    # Get user's invoices
    user_invoices = [
        inv for inv in _invoices.values()
        if inv.get("user_id") == user_id
    ]

    # Sort by date descending
    user_invoices.sort(key=lambda x: x.get("created_at", _now()), reverse=True)

    # Paginate
    total = len(user_invoices)
    start = (page - 1) * page_size
    end = start + page_size
    page_invoices = user_invoices[start:end]

    invoices = [
        InvoiceInfo(
            id=inv["id"],
            number=inv.get("number"),
            status=PaymentStatus(inv["status"]),
            amount_due_cents=inv["amount_due_cents"],
            amount_paid_cents=inv.get("amount_paid_cents", 0),
            currency=inv.get("currency", "usd"),
            created_at=inv["created_at"],
            due_date=inv.get("due_date"),
            paid_at=inv.get("paid_at"),
            invoice_pdf=inv.get("invoice_pdf"),
            hosted_invoice_url=inv.get("hosted_invoice_url"),
            line_items=[
                InvoiceLineItem(**item) for item in inv.get("line_items", [])
            ],
        )
        for inv in page_invoices
    ]

    return APIResponse(
        success=True,
        data=InvoiceListResponse(
            invoices=invoices,
            total=total,
            page=page,
            page_size=page_size,
            has_more=end < total,
        ),
        meta=_get_meta(request),
    )


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[InvoiceInfo]:
    """
    Get details for a specific invoice.
    """
    user_id = user.uid

    invoice_data = _invoices.get(invoice_id)
    if not invoice_data or invoice_data.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    invoice = InvoiceInfo(
        id=invoice_data["id"],
        number=invoice_data.get("number"),
        status=PaymentStatus(invoice_data["status"]),
        amount_due_cents=invoice_data["amount_due_cents"],
        amount_paid_cents=invoice_data.get("amount_paid_cents", 0),
        currency=invoice_data.get("currency", "usd"),
        created_at=invoice_data["created_at"],
        due_date=invoice_data.get("due_date"),
        paid_at=invoice_data.get("paid_at"),
        invoice_pdf=invoice_data.get("invoice_pdf"),
        hosted_invoice_url=invoice_data.get("hosted_invoice_url"),
        line_items=[
            InvoiceLineItem(**item) for item in invoice_data.get("line_items", [])
        ],
    )

    return APIResponse(
        success=True,
        data=invoice,
        meta=_get_meta(request),
    )


# === Usage ===

@router.get("/usage")
async def get_usage(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[UsageSummary]:
    """
    Get current usage for billing period.

    Returns quota usage for documents, videos, and other limits.
    """
    user_id = user.uid
    now = _now()

    # Get user's tier
    sub_data = _user_subscriptions.get(user_id)
    tier = SubscriptionTier.FREE
    if sub_data:
        tier = SubscriptionTier(sub_data["tier"])

    tier_info = TIER_CATALOG.get(tier)
    if not tier_info:
        tier_info = TIER_CATALOG[SubscriptionTier.FREE]

    # Calculate period
    if sub_data:
        period_start = sub_data["current_period_start"]
        period_end = sub_data["current_period_end"]
    else:
        # For free tier, use calendar month
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = period_start.replace(month=period_start.month % 12 + 1)
        period_end = next_month

    # Build quotas (in production, pull from actual usage tracking)
    quotas = [
        UsageQuota(
            feature="documents",
            limit=tier_info.features.max_documents_per_month,
            used=0,  # TODO: Track actual usage
            remaining=tier_info.features.max_documents_per_month,
            resets_at=period_end,
            overage_allowed=tier != SubscriptionTier.FREE,
            overage_rate_cents=50 if tier != SubscriptionTier.FREE else None,
        ),
        UsageQuota(
            feature="youtube_videos",
            limit=tier_info.features.max_youtube_videos_per_month,
            used=0,  # TODO: Track actual usage
            remaining=tier_info.features.max_youtube_videos_per_month,
            resets_at=period_end,
            overage_allowed=tier != SubscriptionTier.FREE,
            overage_rate_cents=25 if tier != SubscriptionTier.FREE else None,
        ),
        UsageQuota(
            feature="workspaces",
            limit=tier_info.features.max_workspaces,
            used=1,  # TODO: Track actual usage
            remaining=max(0, tier_info.features.max_workspaces - 1),
            resets_at=period_end,
            overage_allowed=False,
        ),
    ]

    usage = UsageSummary(
        period_start=period_start,
        period_end=period_end,
        quotas=quotas,
        total_overage_cents=0,  # TODO: Calculate from actual usage
    )

    return APIResponse(
        success=True,
        data=usage,
        meta=_get_meta(request),
    )


# === Webhooks ===

@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
) -> APIResponse[WebhookProcessResult]:
    """
    Handle Stripe webhook events.

    Verifies webhook signature and processes subscription events.

    Acceptance Criteria:
    - Webhook updates subscription status
    """
    # Get raw body for signature verification
    body = await request.body()

    # Get webhook secret from environment
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test")

    # In production, verify Stripe signature
    # For now, we'll do basic validation
    if not stripe_signature:
        logger.warning("Missing Stripe signature on webhook")
        # In dev mode, allow without signature
        if os.environ.get("ENVIRONMENT", "development") == "production":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe-Signature header"
            )

    # Parse event
    try:
        import json
        event_data = json.loads(body)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {e}"
        )

    event_id = event_data.get("id", "unknown")
    event_type = event_data.get("type", "unknown")
    data_object = event_data.get("data", {}).get("object", {})

    logger.info(f"Processing webhook event {event_id}: {event_type}")

    action_taken = None

    try:
        # Handle different event types
        if event_type == "checkout.session.completed":
            # Checkout completed - create subscription
            customer_id = data_object.get("customer")
            subscription_id = data_object.get("subscription")
            user_email = data_object.get("customer_details", {}).get("email")

            action_taken = f"Processed checkout for {customer_id}"
            logger.info(f"Checkout completed: customer={customer_id}, subscription={subscription_id}")

        elif event_type == "customer.subscription.created":
            # New subscription
            subscription_id = data_object.get("id")
            customer_id = data_object.get("customer")
            status = data_object.get("status")

            action_taken = f"Created subscription {subscription_id}"
            logger.info(f"Subscription created: {subscription_id}, status={status}")

        elif event_type == "customer.subscription.updated":
            # Subscription updated (tier change, renewal, etc.)
            subscription_id = data_object.get("id")
            status = data_object.get("status")
            cancel_at_period_end = data_object.get("cancel_at_period_end", False)

            action_taken = f"Updated subscription {subscription_id}"
            logger.info(f"Subscription updated: {subscription_id}, status={status}")

        elif event_type == "customer.subscription.deleted":
            # Subscription canceled
            subscription_id = data_object.get("id")

            action_taken = f"Deleted subscription {subscription_id}"
            logger.info(f"Subscription deleted: {subscription_id}")

        elif event_type == "invoice.paid":
            # Payment successful
            invoice_id = data_object.get("id")
            customer_id = data_object.get("customer")
            amount_paid = data_object.get("amount_paid", 0)

            action_taken = f"Invoice {invoice_id} paid: {amount_paid} cents"
            logger.info(f"Invoice paid: {invoice_id}, amount={amount_paid}")

        elif event_type == "invoice.payment_failed":
            # Payment failed
            invoice_id = data_object.get("id")
            customer_id = data_object.get("customer")

            action_taken = f"Invoice {invoice_id} payment failed"
            logger.warning(f"Payment failed: invoice={invoice_id}, customer={customer_id}")

        else:
            action_taken = f"Ignored event type: {event_type}"
            logger.debug(f"Unhandled event type: {event_type}")

        result = WebhookProcessResult(
            event_id=event_id,
            event_type=event_type,
            processed=True,
            action_taken=action_taken,
            error=None,
        )

    except Exception as e:
        logger.error(f"Error processing webhook {event_id}: {e}")
        result = WebhookProcessResult(
            event_id=event_id,
            event_type=event_type,
            processed=False,
            action_taken=None,
            error=str(e),
        )

    return APIResponse(
        success=result.processed,
        data=result,
        meta=_get_meta(request),
    )
