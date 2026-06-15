from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


BILLING_PLAN_KEYS = [
    "starter",
    "pro",
    "studio",
    "premium",
    "enterprise",
]

BILLING_CYCLES = [
    "monthly",
    "annual",
    "custom",
]

SUBSCRIPTION_STATUSES = [
    "trialing",
    "active",
    "past_due",
    "suspended",
    "cancelled",
    "expired",
    "enterprise_manual",
    "beta",
    "demo",
]

CREDIT_LEDGER_ENTRY_TYPES = [
    "credit_grant",
    "credit_purchase",
    "credit_reserve",
    "credit_release",
    "credit_consume",
    "credit_refund",
    "credit_expire",
    "credit_adjustment",
]

CREDIT_ENTRY_STATUSES = [
    "available",
    "reserved",
    "consumed",
    "expired",
    "refunded",
    "adjusted",
]

BILLING_EVENT_TYPES = [
    "billing_account_created",
    "subscription_started",
    "subscription_upgraded",
    "subscription_downgraded",
    "subscription_cancelled",
    "subscription_past_due",
    "subscription_suspended",
    "payment_provider_synced",
    "invoice_created",
    "invoice_paid",
    "invoice_failed",
    "credit_package_purchased",
    "credits_reserved",
    "credits_consumed",
    "credits_refunded",
    "credits_expired",
    "enterprise_override_applied",
]

PAYMENT_PROVIDER_TYPES = [
    "stripe",
    "manual",
    "none",
]

INVOICE_STATUSES = [
    "draft",
    "open",
    "paid",
    "void",
    "failed",
    "refunded",
]

ENTERPRISE_OVERRIDE_TYPES = [
    "price",
    "credits",
    "modules",
    "storage",
    "users",
    "projects",
    "support",
    "retention",
    "custom",
]

COMMERCIAL_ENTITLEMENT_TYPES = [
    "trial",
    "demo",
    "beta",
]

COMMERCIAL_ENTITLEMENT_STATUSES = [
    "active",
    "expired",
    "revoked",
    "converted",
]

BILLING_ACCOUNT_STATUSES = [
    "active",
    "closed",
]

CREDIT_PACKAGE_PURCHASE_STATUSES = [
    "active",
    "consumed",
    "expired",
    "refunded",
    "revoked",
]


def _enum_ck(column_name: str, values: list[str]) -> str:
    """Build a CheckConstraint SQL fragment: column IN ('a', 'b', ...)."""
    if not values:
        raise ValueError(f"Cannot build check constraint with empty values for {column_name}")
    quoted = ", ".join(repr(v) for v in values)
    return f"{column_name} IN ({quoted})"


def _uuid_hex() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.utcnow()


class BillingAccount(Base):
    __tablename__ = "billing_accounts"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("status", BILLING_ACCOUNT_STATUSES),
            name="ck_billing_accounts_status",
        ),
        CheckConstraint(
            "closed_at IS NULL OR closed_at >= created_at",
            name="ck_billing_accounts_closed_after_created",
        ),
        UniqueConstraint("organization_id", name="uq_billing_accounts_organization_id"),
        Index("ix_billing_accounts_status", "status"),
        Index("ix_billing_accounts_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    billing_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    default_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="es-ES")
    fiscal_address_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CIDSubscription(Base):
    __tablename__ = "cid_subscriptions"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_cid_subscriptions_plan_key",
        ),
        CheckConstraint(
            _enum_ck("billing_cycle", BILLING_CYCLES),
            name="ck_cid_subscriptions_billing_cycle",
        ),
        CheckConstraint(
            _enum_ck("current_status", SUBSCRIPTION_STATUSES),
            name="ck_cid_subscriptions_current_status",
        ),
        Index("ix_cid_subscriptions_billing_account_id", "billing_account_id"),
        Index("ix_cid_subscriptions_plan_key", "plan_key"),
        Index("ix_cid_subscriptions_current_status", "current_status"),
        Index("ix_cid_subscriptions_next_renewal_at", "next_renewal_at"),
        Index("ix_cid_subscriptions_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    billing_account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    plan_key: Mapped[str] = mapped_column(String(30), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")
    current_status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    plan_snapshot_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_renewal_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trial_end_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancellation_effective_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    grace_period_end_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    enterprise_override_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    entitlement_flags_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )


class PlanSnapshot(Base):
    __tablename__ = "plan_snapshots"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_plan_snapshots_plan_key",
        ),
        CheckConstraint(
            _enum_ck("billing_cycle", BILLING_CYCLES),
            name="ck_plan_snapshots_billing_cycle",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_plan_snapshots_effective_to_after_from",
        ),
        Index("ix_plan_snapshots_plan_key", "plan_key"),
        Index("ix_plan_snapshots_billing_cycle", "billing_cycle"),
        Index("ix_plan_snapshots_canon_version", "canon_version"),
        Index("ix_plan_snapshots_effective_from", "effective_from"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    plan_key: Mapped[str] = mapped_column(String(30), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    credits_included_per_period: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    users_included: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    projects_active_max: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_gb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    concurrent_ai_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    modules_included_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    modules_limited_quotas_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    exports_per_period: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    support_tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    audit_retention_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data_retention_days_after_cancellation: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    ai_traceability_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    canon_version: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class PlanChangeHistory(Base):
    __tablename__ = "plan_change_history"
    __table_args__ = (
        Index("ix_plan_change_history_subscription_id", "subscription_id"),
        Index("ix_plan_change_history_to_snapshot", "to_plan_snapshot_id"),
        Index("ix_plan_change_history_actor_id", "actor_id"),
        Index("ix_plan_change_history_effective_at", "effective_at"),
        Index("ix_plan_change_history_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    subscription_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    from_plan_snapshot_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    to_plan_snapshot_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pro_rata_amount_eur: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    credit_balance_carried_eur: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class CreditBalance(Base):
    __tablename__ = "credit_balances"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_credit_balances_organization_id"),
        CheckConstraint(
            "included_monthly_remaining >= 0 AND purchased_balance >= 0 AND "
            "promotional_balance >= 0 AND trial_balance >= 0 AND "
            "enterprise_balance >= 0 AND reserved_active >= 0",
            name="ck_credit_balances_non_negative_subbalances",
        ),
        CheckConstraint(
            "consumed_period >= 0 AND expired_total >= 0 AND "
            "refunded_total >= 0 AND version >= 1",
            name="ck_credit_balances_non_negative_counters",
        ),
        Index("ix_credit_balances_organization_id", "organization_id"),
        Index("ix_credit_balances_last_updated_at", "last_updated_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    included_monthly_remaining: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    purchased_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    promotional_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trial_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enterprise_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_active: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consumed_period: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expired_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    refunded_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    adjusted_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class CreditLedgerEntry(Base):
    __tablename__ = "credit_ledger_entries"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("entry_type", CREDIT_LEDGER_ENTRY_TYPES),
            name="ck_credit_ledger_entries_entry_type",
        ),
        CheckConstraint(
            _enum_ck("status", CREDIT_ENTRY_STATUSES),
            name="ck_credit_ledger_entries_status",
        ),
        CheckConstraint(
            "amount <> 0",
            name="ck_credit_ledger_entries_amount_nonzero",
        ),
        UniqueConstraint("idempotency_key", name="uq_credit_ledger_entries_idempotency_key"),
        Index("ix_credit_ledger_entries_organization_id", "organization_id"),
        Index("ix_credit_ledger_entries_project_id", "project_id"),
        Index("ix_credit_ledger_entries_user_id", "user_id"),
        Index("ix_credit_ledger_entries_job_id", "job_id"),
        Index("ix_credit_ledger_entries_subscription_id", "subscription_id"),
        Index("ix_credit_ledger_entries_package_purchase_id", "credit_package_purchase_id"),
        Index("ix_credit_ledger_entries_entry_type", "entry_type"),
        Index("ix_credit_ledger_entries_status", "status"),
        Index("ix_credit_ledger_entries_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    credit_package_purchase_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )
    entry_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reserved_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class CreditPackagePurchase(Base):
    __tablename__ = "credit_package_purchases"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("compatible_plan_key", BILLING_PLAN_KEYS),
            name="ck_credit_package_purchases_compatible_plan_key",
        ),
        CheckConstraint(
            _enum_ck("status", CREDIT_PACKAGE_PURCHASE_STATUSES),
            name="ck_credit_package_purchases_status",
        ),
        CheckConstraint(
            "credits > 0",
            name="ck_credit_package_purchases_credits_positive",
        ),
        Index("ix_credit_package_purchases_organization_id", "organization_id"),
        Index("ix_credit_package_purchases_billing_account_id", "billing_account_id"),
        Index("ix_credit_package_purchases_subscription_id", "subscription_id"),
        Index("ix_credit_package_purchases_package_key", "package_key"),
        Index("ix_credit_package_purchases_status", "status"),
        Index("ix_credit_package_purchases_provider_reference_id", "provider_reference_id"),
        Index("ix_credit_package_purchases_invoice_reference_id", "invoice_reference_id"),
        Index("ix_credit_package_purchases_expires_at", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    billing_account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    package_key: Mapped[str] = mapped_column(String(80), nullable=False)
    compatible_plan_key: Mapped[str] = mapped_column(String(30), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    price_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")
    purchased_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    provider_reference_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    invoice_reference_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)


class InvoiceReference(Base):
    __tablename__ = "invoice_references"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("provider_type", PAYMENT_PROVIDER_TYPES),
            name="ck_invoice_references_provider_type",
        ),
        CheckConstraint(
            _enum_ck("status", INVOICE_STATUSES),
            name="ck_invoice_references_status",
        ),
        Index("ix_invoice_references_billing_account_id", "billing_account_id"),
        Index("ix_invoice_references_subscription_id", "subscription_id"),
        Index("ix_invoice_references_provider_reference_id", "provider_reference_id"),
        Index("ix_invoice_references_provider_invoice_id", "provider_invoice_id"),
        Index("ix_invoice_references_status", "status"),
        Index("ix_invoice_references_issued_at", "issued_at"),
        Index("ix_invoice_references_paid_at", "paid_at"),
        Index("ix_invoice_references_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    billing_account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    provider_reference_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    provider_type: Mapped[str] = mapped_column(String(30), nullable=False, default="stripe")
    provider_invoice_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")
    amount_subtotal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    amount_tax: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    amount_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tax_country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    hosted_invoice_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    issued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class PaymentProviderReference(Base):
    __tablename__ = "payment_provider_references"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("provider_type", PAYMENT_PROVIDER_TYPES),
            name="ck_payment_provider_references_provider_type",
        ),
        UniqueConstraint(
            "provider_event_id", name="uq_payment_provider_references_provider_event_id"
        ),
        Index("ix_payment_provider_references_billing_account_id", "billing_account_id"),
        Index("ix_payment_provider_references_subscription_id", "subscription_id"),
        Index("ix_payment_provider_references_stripe_customer_id", "stripe_customer_id"),
        Index("ix_payment_provider_references_stripe_subscription_id", "stripe_subscription_id"),
        Index("ix_payment_provider_references_provider_type", "provider_type"),
        Index("ix_payment_provider_references_last_synced_at", "last_synced_at"),
        Index("ix_payment_provider_references_updated_at", "updated_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    billing_account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    provider_type: Mapped[str] = mapped_column(String(30), nullable=False, default="stripe")
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_product_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_event_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )


class EnterpriseOverride(Base):
    __tablename__ = "enterprise_overrides"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("override_type", ENTERPRISE_OVERRIDE_TYPES),
            name="ck_enterprise_overrides_override_type",
        ),
        CheckConstraint(
            "ends_at IS NULL OR ends_at >= starts_at",
            name="ck_enterprise_overrides_ends_at_after_starts_at",
        ),
        Index("ix_enterprise_overrides_organization_id", "organization_id"),
        Index("ix_enterprise_overrides_billing_account_id", "billing_account_id"),
        Index("ix_enterprise_overrides_subscription_id", "subscription_id"),
        Index("ix_enterprise_overrides_override_type", "override_type"),
        Index("ix_enterprise_overrides_active", "active"),
        Index("ix_enterprise_overrides_approved_by_user_id", "approved_by_user_id"),
        Index("ix_enterprise_overrides_starts_at", "starts_at"),
        Index("ix_enterprise_overrides_ends_at", "ends_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    billing_account_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    override_type: Mapped[str] = mapped_column(String(50), nullable=False)
    override_value_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )


class BillingEvent(Base):
    __tablename__ = "billing_events"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("event_type", BILLING_EVENT_TYPES),
            name="ck_billing_events_event_type",
        ),
        Index("ix_billing_events_organization_id", "organization_id"),
        Index("ix_billing_events_billing_account_id", "billing_account_id"),
        Index("ix_billing_events_subscription_id", "subscription_id"),
        Index("ix_billing_events_event_type", "event_type"),
        Index("ix_billing_events_actor_id", "actor_id"),
        Index("ix_billing_events_provider_event_id", "provider_event_id"),
        Index("ix_billing_events_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    billing_account_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    provider_event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class TrialEntitlement(Base):
    __tablename__ = "trial_entitlements"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_trial_entitlements_plan_key",
        ),
        CheckConstraint(
            _enum_ck("status", COMMERCIAL_ENTITLEMENT_STATUSES),
            name="ck_trial_entitlements_status",
        ),
        CheckConstraint(
            "ends_at >= starts_at",
            name="ck_trial_entitlements_ends_at_after_starts_at",
        ),
        Index("ix_trial_entitlements_organization_id", "organization_id"),
        Index("ix_trial_entitlements_subscription_id", "subscription_id"),
        Index("ix_trial_entitlements_status", "status"),
        Index("ix_trial_entitlements_ends_at", "ends_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    plan_key: Mapped[str] = mapped_column(String(30), nullable=False, default="pro")
    trial_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    requires_card: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class DemoEntitlement(Base):
    __tablename__ = "demo_entitlements"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("status", COMMERCIAL_ENTITLEMENT_STATUSES),
            name="ck_demo_entitlements_status",
        ),
        CheckConstraint(
            "plan_key IS NULL OR " + _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_demo_entitlements_plan_key",
        ),
        CheckConstraint(
            "conversion_target_plan IS NULL OR "
            + _enum_ck("conversion_target_plan", BILLING_PLAN_KEYS),
            name="ck_demo_entitlements_conversion_target_plan",
        ),
        Index("ix_demo_entitlements_organization_id", "organization_id"),
        Index("ix_demo_entitlements_granted_by_user_id", "granted_by_user_id"),
        Index("ix_demo_entitlements_status", "status"),
        Index("ix_demo_entitlements_ends_at", "ends_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    granted_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    plan_key: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    manual_limits_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    demo_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    conversion_target_plan: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class BetaEntitlement(Base):
    __tablename__ = "beta_entitlements"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_beta_entitlements_plan_key",
        ),
        CheckConstraint(
            _enum_ck("status", COMMERCIAL_ENTITLEMENT_STATUSES),
            name="ck_beta_entitlements_status",
        ),
        CheckConstraint(
            "ends_at >= starts_at",
            name="ck_beta_entitlements_ends_at_after_starts_at",
        ),
        Index("ix_beta_entitlements_organization_id", "organization_id"),
        Index("ix_beta_entitlements_beta_program_key", "beta_program_key"),
        Index("ix_beta_entitlements_status", "status"),
        Index("ix_beta_entitlements_ends_at", "ends_at"),
        Index("ix_beta_entitlements_converted_subscription_id", "converted_subscription_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    beta_program_key: Mapped[str] = mapped_column(String(80), nullable=False)
    feedback_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    plan_key: Mapped[str] = mapped_column(String(30), nullable=False, default="pro")
    beta_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    converted_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


__all__ = [
    "BILLING_PLAN_KEYS",
    "BILLING_CYCLES",
    "SUBSCRIPTION_STATUSES",
    "CREDIT_LEDGER_ENTRY_TYPES",
    "CREDIT_ENTRY_STATUSES",
    "BILLING_EVENT_TYPES",
    "PAYMENT_PROVIDER_TYPES",
    "INVOICE_STATUSES",
    "ENTERPRISE_OVERRIDE_TYPES",
    "COMMERCIAL_ENTITLEMENT_TYPES",
    "COMMERCIAL_ENTITLEMENT_STATUSES",
    "BILLING_ACCOUNT_STATUSES",
    "CREDIT_PACKAGE_PURCHASE_STATUSES",
    "_enum_ck",
    "BillingAccount",
    "CIDSubscription",
    "PlanSnapshot",
    "PlanChangeHistory",
    "CreditBalance",
    "CreditLedgerEntry",
    "CreditPackagePurchase",
    "InvoiceReference",
    "PaymentProviderReference",
    "EnterpriseOverride",
    "BillingEvent",
    "TrialEntitlement",
    "DemoEntitlement",
    "BetaEntitlement",
]
