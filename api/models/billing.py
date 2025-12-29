"""
Stripe Billing Models

Pydantic models for subscription and billing management.
Supports checkout sessions, customer portal, webhooks, and subscription status.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    """Available subscription tiers."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Stripe subscription statuses."""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    PAUSED = "paused"


class PaymentStatus(str, Enum):
    """Payment status for invoices."""
    PAID = "paid"
    UNPAID = "unpaid"
    NO_PAYMENT_REQUIRED = "no_payment_required"
    DRAFT = "draft"
    OPEN = "open"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class BillingInterval(str, Enum):
    """Billing interval options."""
    MONTHLY = "month"
    YEARLY = "year"


# === Tier Definitions ===

class TierFeatures(BaseModel):
    """Features included in a subscription tier."""
    max_workspaces: int = Field(..., description="Maximum number of workspaces")
    max_members_per_workspace: int = Field(..., description="Max members per workspace")
    max_documents_per_month: int = Field(..., description="Monthly document processing limit")
    max_youtube_videos_per_month: int = Field(..., description="Monthly YouTube processing limit")
    ai_model: str = Field(..., description="AI model tier (haiku, sonnet, opus)")
    knowledge_stores: List[str] = Field(..., description="Available knowledge stores")
    integrations: List[str] = Field(..., description="Available integrations")
    support_level: str = Field(..., description="Support tier (community, email, priority)")
    custom_skills: bool = Field(default=False, description="Can create custom skills")
    voice_notifications: bool = Field(default=False, description="Voice notification support")
    api_access: bool = Field(default=False, description="Direct API access")


class TierPricing(BaseModel):
    """Pricing for a subscription tier."""
    monthly_price_cents: int = Field(..., description="Monthly price in cents")
    yearly_price_cents: int = Field(..., description="Yearly price in cents")
    yearly_discount_percent: int = Field(default=0, description="Discount for yearly billing")
    stripe_price_id_monthly: Optional[str] = Field(None, description="Stripe price ID for monthly")
    stripe_price_id_yearly: Optional[str] = Field(None, description="Stripe price ID for yearly")


class SubscriptionTierInfo(BaseModel):
    """Complete tier information."""
    tier: SubscriptionTier = Field(..., description="Tier identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Tier description")
    features: TierFeatures = Field(..., description="Included features")
    pricing: TierPricing = Field(..., description="Pricing details")
    is_popular: bool = Field(default=False, description="Highlight as popular choice")


# === Customer & Subscription ===

class CustomerInfo(BaseModel):
    """Stripe customer information."""
    stripe_customer_id: str = Field(..., description="Stripe customer ID")
    email: str = Field(..., description="Billing email")
    name: Optional[str] = Field(None, description="Customer name")
    created_at: datetime = Field(..., description="When customer was created")
    default_payment_method: Optional[str] = Field(None, description="Default payment method ID")
    currency: str = Field(default="usd", description="Default currency")


class SubscriptionInfo(BaseModel):
    """Current subscription details."""
    id: str = Field(..., description="Subscription ID")
    status: SubscriptionStatus = Field(..., description="Current status")
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    billing_interval: BillingInterval = Field(..., description="Billing interval")
    current_period_start: datetime = Field(..., description="Current period start")
    current_period_end: datetime = Field(..., description="Current period end")
    cancel_at_period_end: bool = Field(default=False, description="Will cancel at period end")
    canceled_at: Optional[datetime] = Field(None, description="When canceled (if applicable)")
    trial_end: Optional[datetime] = Field(None, description="Trial end date (if applicable)")


class BillingOverview(BaseModel):
    """Complete billing overview for a user/workspace."""
    customer: Optional[CustomerInfo] = Field(None, description="Customer info if exists")
    subscription: Optional[SubscriptionInfo] = Field(None, description="Active subscription")
    tier: SubscriptionTier = Field(default=SubscriptionTier.FREE, description="Current tier")
    is_trial: bool = Field(default=False, description="Currently on trial")
    trial_days_remaining: Optional[int] = Field(None, description="Days remaining in trial")
    next_invoice_date: Optional[datetime] = Field(None, description="Next invoice date")
    next_invoice_amount_cents: Optional[int] = Field(None, description="Next invoice amount")


# === Checkout ===

class CheckoutSessionRequest(BaseModel):
    """Request to create a checkout session."""
    tier: SubscriptionTier = Field(..., description="Target subscription tier")
    billing_interval: BillingInterval = Field(
        default=BillingInterval.MONTHLY,
        description="Billing interval"
    )
    success_url: str = Field(..., description="URL to redirect on success")
    cancel_url: str = Field(..., description="URL to redirect on cancel")
    promotion_code: Optional[str] = Field(None, description="Optional promotion code")
    trial_days: Optional[int] = Field(None, description="Trial period in days")


class CheckoutSessionResponse(BaseModel):
    """Response with checkout session URL."""
    checkout_url: str = Field(..., description="Stripe checkout URL to redirect user")
    session_id: str = Field(..., description="Checkout session ID")
    expires_at: datetime = Field(..., description="When session expires")


# === Portal ===

class PortalSessionRequest(BaseModel):
    """Request to create a customer portal session."""
    return_url: str = Field(..., description="URL to return after portal")


class PortalSessionResponse(BaseModel):
    """Response with customer portal URL."""
    portal_url: str = Field(..., description="Stripe portal URL to redirect user")
    expires_at: Optional[datetime] = Field(None, description="When session expires")


# === Invoices ===

class InvoiceLineItem(BaseModel):
    """Line item on an invoice."""
    description: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity")
    unit_amount_cents: int = Field(..., description="Unit price in cents")
    total_cents: int = Field(..., description="Line total in cents")


class InvoiceInfo(BaseModel):
    """Invoice details."""
    id: str = Field(..., description="Invoice ID")
    number: Optional[str] = Field(None, description="Invoice number")
    status: PaymentStatus = Field(..., description="Payment status")
    amount_due_cents: int = Field(..., description="Amount due in cents")
    amount_paid_cents: int = Field(default=0, description="Amount paid in cents")
    currency: str = Field(default="usd", description="Currency")
    created_at: datetime = Field(..., description="Invoice creation date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    paid_at: Optional[datetime] = Field(None, description="When paid")
    invoice_pdf: Optional[str] = Field(None, description="PDF download URL")
    hosted_invoice_url: Optional[str] = Field(None, description="Stripe hosted invoice URL")
    line_items: List[InvoiceLineItem] = Field(
        default_factory=list,
        description="Line items"
    )


class InvoiceListResponse(BaseModel):
    """Paginated list of invoices."""
    invoices: List[InvoiceInfo]
    total: int = Field(..., description="Total invoices")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=10, description="Items per page")
    has_more: bool = Field(default=False, description="More pages available")


# === Webhooks ===

class WebhookEventType(str, Enum):
    """Stripe webhook event types we handle."""
    CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"
    CHECKOUT_SESSION_EXPIRED = "checkout.session.expired"
    CUSTOMER_SUBSCRIPTION_CREATED = "customer.subscription.created"
    CUSTOMER_SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    CUSTOMER_SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"


class WebhookProcessResult(BaseModel):
    """Result of processing a webhook."""
    event_id: str = Field(..., description="Stripe event ID")
    event_type: str = Field(..., description="Event type")
    processed: bool = Field(..., description="Whether event was processed")
    action_taken: Optional[str] = Field(None, description="What action was taken")
    error: Optional[str] = Field(None, description="Error if processing failed")


# === Usage ===

class UsageQuota(BaseModel):
    """Usage quota for a feature."""
    feature: str = Field(..., description="Feature name")
    limit: int = Field(..., description="Monthly limit")
    used: int = Field(..., description="Amount used this period")
    remaining: int = Field(..., description="Amount remaining")
    resets_at: datetime = Field(..., description="When quota resets")
    overage_allowed: bool = Field(default=False, description="Can exceed limit")
    overage_rate_cents: Optional[int] = Field(None, description="Rate per overage unit")


class UsageSummary(BaseModel):
    """Summary of usage for billing period."""
    period_start: datetime = Field(..., description="Billing period start")
    period_end: datetime = Field(..., description="Billing period end")
    quotas: List[UsageQuota] = Field(default_factory=list, description="Usage quotas")
    total_overage_cents: int = Field(default=0, description="Total overage charges")


# === Tier Change ===

class TierChangePreview(BaseModel):
    """Preview of a tier change."""
    current_tier: SubscriptionTier = Field(..., description="Current tier")
    target_tier: SubscriptionTier = Field(..., description="Target tier")
    is_upgrade: bool = Field(..., description="Whether this is an upgrade")
    immediate_charge_cents: Optional[int] = Field(
        None,
        description="Amount charged immediately (prorated)"
    )
    credit_cents: Optional[int] = Field(
        None,
        description="Credit applied (if downgrading)"
    )
    new_monthly_amount_cents: int = Field(..., description="New monthly charge")
    effective_date: datetime = Field(..., description="When change takes effect")
    features_gained: List[str] = Field(
        default_factory=list,
        description="Features gained in upgrade"
    )
    features_lost: List[str] = Field(
        default_factory=list,
        description="Features lost in downgrade"
    )


class TierChangeRequest(BaseModel):
    """Request to change subscription tier."""
    target_tier: SubscriptionTier = Field(..., description="New tier")
    billing_interval: Optional[BillingInterval] = Field(
        None,
        description="New billing interval (optional)"
    )
    immediate: bool = Field(
        default=False,
        description="Apply immediately vs at period end"
    )


class TierChangeResponse(BaseModel):
    """Response after tier change."""
    success: bool = Field(..., description="Whether change succeeded")
    subscription: SubscriptionInfo = Field(..., description="Updated subscription")
    message: str = Field(..., description="Status message")
    invoice_id: Optional[str] = Field(None, description="Invoice for immediate charges")


# === Cancel ===

class CancelRequest(BaseModel):
    """Request to cancel subscription."""
    reason: Optional[str] = Field(None, description="Cancellation reason")
    feedback: Optional[str] = Field(None, description="Additional feedback")
    immediate: bool = Field(
        default=False,
        description="Cancel immediately vs at period end"
    )


class CancelResponse(BaseModel):
    """Response after cancellation."""
    success: bool = Field(..., description="Whether cancellation succeeded")
    cancel_at: Optional[datetime] = Field(None, description="When subscription ends")
    message: str = Field(..., description="Status message")
