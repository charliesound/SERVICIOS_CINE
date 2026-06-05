from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BillingAccountBase(BaseModel):
    organization_id: str
    legal_name: str | None = None
    tax_id: str | None = None
    billing_email: str | None = None
    country: str | None = None
    default_currency: str = "EUR"
    language: str = "es-ES"
    fiscal_address_json: dict[str, Any] | None = None
    status: str = "active"


class BillingAccountCreate(BillingAccountBase):
    pass


class BillingAccountRead(BillingAccountBase):
    id: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SubscriptionRead(BaseModel):
    id: str
    billing_account_id: str
    organization_id: str
    plan_key: str
    billing_cycle: str = "monthly"
    currency: str = "EUR"
    current_status: str
    plan_snapshot_id: str | None = None
    start_at: datetime
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    next_renewal_at: datetime | None = None
    trial_end_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_effective_at: datetime | None = None
    auto_renew: bool = True
    grace_period_end_at: datetime | None = None
    enterprise_override_id: str | None = None
    entitlement_flags_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanSnapshotRead(BaseModel):
    id: str
    plan_key: str
    display_name: str
    price_amount: float | None = None
    price_currency: str = "EUR"
    billing_cycle: str
    credits_included_per_period: int = 0
    users_included: int = 0
    projects_active_max: int = 0
    storage_gb: float = 0.0
    concurrent_ai_jobs: int = 0
    modules_included_json: dict[str, Any] | None = None
    modules_limited_quotas_json: dict[str, Any] | None = None
    exports_per_period: int = 0
    support_tier: str | None = None
    audit_retention_days: int | None = None
    data_retention_days_after_cancellation: int | None = None
    ai_traceability_level: str | None = None
    canon_version: str
    effective_from: datetime
    effective_to: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanChangeHistoryRead(BaseModel):
    id: str
    subscription_id: str
    from_plan_snapshot_id: str | None = None
    to_plan_snapshot_id: str
    change_type: str
    effective_at: datetime
    pro_rata_amount_eur: float | None = None
    credit_balance_carried_eur: float | None = None
    actor_id: str | None = None
    reason: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreditBalanceRead(BaseModel):
    id: str
    organization_id: str
    included_monthly_remaining: int = 0
    purchased_balance: int = 0
    promotional_balance: int = 0
    trial_balance: int = 0
    enterprise_balance: int = 0
    reserved_active: int = 0
    consumed_period: int = 0
    expired_total: int = 0
    refunded_total: int = 0
    adjusted_total: int = 0
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    last_updated_at: datetime
    version: int = 1

    model_config = ConfigDict(from_attributes=True)


class CreditLedgerEntryRead(BaseModel):
    id: str
    organization_id: str
    project_id: str | None = None
    user_id: str | None = None
    job_id: str | None = None
    subscription_id: str | None = None
    credit_package_purchase_id: str | None = None
    entry_type: str
    status: str
    amount: int
    balance_after: int | None = None
    reason: str | None = None
    idempotency_key: str | None = None
    expires_at: datetime | None = None
    reserved_until: datetime | None = None
    released_at: datetime | None = None
    consumed_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreditPackagePurchaseRead(BaseModel):
    id: str
    organization_id: str
    billing_account_id: str
    subscription_id: str | None = None
    package_key: str
    compatible_plan_key: str
    credits: int
    price_amount: float | None = None
    price_currency: str = "EUR"
    purchased_at: datetime
    expires_at: datetime | None = None
    provider_reference_id: str | None = None
    invoice_reference_id: str | None = None
    status: str = "active"
    metadata_json: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceReferenceRead(BaseModel):
    id: str
    billing_account_id: str
    subscription_id: str | None = None
    provider_reference_id: str | None = None
    provider_type: str = "stripe"
    provider_invoice_id: str | None = None
    invoice_number: str | None = None
    status: str
    currency: str = "EUR"
    amount_subtotal: float | None = None
    amount_tax: float | None = None
    amount_total: float | None = None
    tax_country: str | None = None
    pdf_url: str | None = None
    hosted_invoice_url: str | None = None
    issued_at: datetime | None = None
    paid_at: datetime | None = None
    failed_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentProviderReferenceRead(BaseModel):
    id: str
    billing_account_id: str
    subscription_id: str | None = None
    provider_type: str = "stripe"
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    stripe_price_id: str | None = None
    stripe_product_id: str | None = None
    stripe_invoice_id: str | None = None
    stripe_payment_intent_id: str | None = None
    provider_event_id: str | None = None
    provider_event_hash: str | None = None
    last_synced_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnterpriseOverrideRead(BaseModel):
    id: str
    organization_id: str
    billing_account_id: str | None = None
    subscription_id: str | None = None
    override_type: str
    override_value_json: dict[str, Any] | None = None
    reason: str | None = None
    approved_by_user_id: str
    starts_at: datetime
    ends_at: datetime | None = None
    active: bool = True
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillingEventRead(BaseModel):
    id: str
    organization_id: str
    billing_account_id: str | None = None
    subscription_id: str | None = None
    event_type: str
    from_status: str | None = None
    to_status: str | None = None
    actor_id: str | None = None
    provider_event_id: str | None = None
    reason: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrialEntitlementRead(BaseModel):
    id: str
    organization_id: str
    subscription_id: str | None = None
    plan_key: str = "pro"
    trial_balance: int = 0
    starts_at: datetime
    ends_at: datetime
    status: str = "active"
    requires_card: bool = True
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DemoEntitlementRead(BaseModel):
    id: str
    organization_id: str
    granted_by_user_id: str | None = None
    plan_key: str | None = None
    manual_limits_json: dict[str, Any] | None = None
    demo_balance: int = 0
    starts_at: datetime
    ends_at: datetime | None = None
    status: str = "active"
    conversion_target_plan: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BetaEntitlementRead(BaseModel):
    id: str
    organization_id: str
    beta_program_key: str
    feedback_required: bool = True
    plan_key: str = "pro"
    beta_balance: int = 0
    starts_at: datetime
    ends_at: datetime
    status: str = "active"
    converted_subscription_id: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillingBlockCode(str, Enum):
    billing_inactive = "billing_inactive"
    subscription_past_due = "subscription_past_due"
    subscription_suspended = "subscription_suspended"
    plan_not_active = "plan_not_active"
    module_not_included = "module_not_included"
    add_on_required = "add_on_required"
    credits_exhausted = "credits_exhausted"
    storage_exhausted = "storage_exhausted"
    seat_limit_reached = "seat_limit_reached"
    project_limit_reached = "project_limit_reached"
    enterprise_only = "enterprise_only"
    provider_sync_pending = "provider_sync_pending"


class BillingBlockCta(BaseModel):
    label: str
    url: str | None = None
    action: str | None = None


class BillingBlockResponse(BaseModel):
    code: BillingBlockCode
    http_status: int = 402
    message: str
    cta: BillingBlockCta | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None
    billing_event_id: str | None = None


class BillingCapabilitiesResponse(BaseModel):
    organization_id: str
    plan_key: str
    current_status: str
    can_submit_ai_jobs: bool
    can_export: bool
    can_invite_users: bool
    can_create_projects: bool
    available_credit_balance: int
    reserved_active: int
    monthly_credits_remaining: int
    purchased_balance: int
    trial_balance: int
    promotional_balance: int
    enterprise_balance: int
    blocked_reasons: list[BillingBlockCode] = Field(default_factory=list)
    active_override_types: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "BillingAccountBase",
    "BillingAccountCreate",
    "BillingAccountRead",
    "SubscriptionRead",
    "PlanSnapshotRead",
    "PlanChangeHistoryRead",
    "CreditBalanceRead",
    "CreditLedgerEntryRead",
    "CreditPackagePurchaseRead",
    "InvoiceReferenceRead",
    "PaymentProviderReferenceRead",
    "EnterpriseOverrideRead",
    "BillingEventRead",
    "TrialEntitlementRead",
    "DemoEntitlementRead",
    "BetaEntitlementRead",
    "BillingBlockCode",
    "BillingBlockCta",
    "BillingBlockResponse",
    "BillingCapabilitiesResponse",
]
