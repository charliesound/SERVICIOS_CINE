"""add cid billing models

Revision ID: 20260605_000001_billing
Revises: c97a97e2e3a8
Create Date: 2026-06-05 12:00:00.000000

This migration creates the 14 billing tables defined in src/models/billing.py:

1. billing_accounts
2. cid_subscriptions
3. plan_snapshots
4. plan_change_history
5. credit_balances
6. credit_ledger_entries
7. credit_package_purchases
8. invoice_references
9. payment_provider_references
10. enterprise_overrides
11. billing_events
12. trial_entitlements
13. demo_entitlements
14. beta_entitlements

DDL, indices and check constraints are mirrored from the ORM models. No data
backfill is included. No Stripe or external provider is wired.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260605_000001_billing"
down_revision = "c97a97e2e3a8"
branch_labels = None
depends_on = None


BILLING_PLAN_KEYS = (
    "starter",
    "pro",
    "studio",
    "premium",
    "enterprise",
)

BILLING_CYCLES = (
    "monthly",
    "annual",
    "custom",
)

SUBSCRIPTION_STATUSES = (
    "trialing",
    "active",
    "past_due",
    "suspended",
    "cancelled",
    "expired",
    "enterprise_manual",
    "beta",
    "demo",
)

CREDIT_LEDGER_ENTRY_TYPES = (
    "credit_grant",
    "credit_purchase",
    "credit_reserve",
    "credit_release",
    "credit_consume",
    "credit_refund",
    "credit_expire",
    "credit_adjustment",
)

CREDIT_ENTRY_STATUSES = (
    "available",
    "reserved",
    "consumed",
    "expired",
    "refunded",
    "adjusted",
)

BILLING_EVENT_TYPES = (
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
)

PAYMENT_PROVIDER_TYPES = (
    "stripe",
    "manual",
    "none",
)

INVOICE_STATUSES = (
    "draft",
    "open",
    "paid",
    "void",
    "failed",
    "refunded",
)

ENTERPRISE_OVERRIDE_TYPES = (
    "price",
    "credits",
    "modules",
    "storage",
    "users",
    "projects",
    "support",
    "retention",
    "custom",
)

COMMERCIAL_ENTITLEMENT_STATUSES = (
    "active",
    "expired",
    "revoked",
    "converted",
)

BILLING_ACCOUNT_STATUSES = (
    "active",
    "closed",
)

CREDIT_PACKAGE_PURCHASE_STATUSES = (
    "active",
    "consumed",
    "expired",
    "refunded",
    "revoked",
)


def _enum_in_list(values):
    return ", ".join("'{}'".format(v.replace("'", "''")) for v in values)


def _enum_ck(column_name, values):
    return "{} IN ({})".format(column_name, _enum_in_list(values))


def upgrade() -> None:
    # 1. billing_accounts
    op.create_table(
        "billing_accounts",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("legal_name", sa.String(255), nullable=True),
        sa.Column("tax_id", sa.String(100), nullable=True),
        sa.Column("billing_email", sa.String(255), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("default_currency", sa.String(10), nullable=False, server_default="EUR"),
        sa.Column("language", sa.String(20), nullable=False, server_default="es-ES"),
        sa.Column("fiscal_address_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            _enum_ck("status", BILLING_ACCOUNT_STATUSES),
            name="ck_billing_accounts_status",
        ),
        sa.CheckConstraint(
            "closed_at IS NULL OR closed_at >= created_at",
            name="ck_billing_accounts_closed_after_created",
        ),
        sa.UniqueConstraint("organization_id", name="uq_billing_accounts_organization_id"),
    )
    op.create_index("ix_billing_accounts_organization_id", "billing_accounts", ["organization_id"])
    op.create_index("ix_billing_accounts_status", "billing_accounts", ["status"])
    op.create_index("ix_billing_accounts_created_at", "billing_accounts", ["created_at"])

    # 2. cid_subscriptions
    op.create_table(
        "cid_subscriptions",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("billing_account_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("plan_key", sa.String(30), nullable=False),
        sa.Column("billing_cycle", sa.String(20), nullable=False, server_default="monthly"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="EUR"),
        sa.Column("current_status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("plan_snapshot_id", sa.String(36), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("current_period_start", sa.DateTime(), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("next_renewal_at", sa.DateTime(), nullable=True),
        sa.Column("trial_end_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("cancellation_effective_at", sa.DateTime(), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("grace_period_end_at", sa.DateTime(), nullable=True),
        sa.Column("enterprise_override_id", sa.String(36), nullable=True),
        sa.Column("entitlement_flags_json", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_cid_subscriptions_plan_key",
        ),
        sa.CheckConstraint(
            _enum_ck("billing_cycle", BILLING_CYCLES),
            name="ck_cid_subscriptions_billing_cycle",
        ),
        sa.CheckConstraint(
            _enum_ck("current_status", SUBSCRIPTION_STATUSES),
            name="ck_cid_subscriptions_current_status",
        ),
    )
    op.create_index(
        "ix_cid_subscriptions_billing_account_id", "cid_subscriptions", ["billing_account_id"]
    )
    op.create_index("ix_cid_subscriptions_organization_id", "cid_subscriptions", ["organization_id"])
    op.create_index("ix_cid_subscriptions_plan_key", "cid_subscriptions", ["plan_key"])
    op.create_index("ix_cid_subscriptions_current_status", "cid_subscriptions", ["current_status"])
    op.create_index("ix_cid_subscriptions_plan_snapshot_id", "cid_subscriptions", ["plan_snapshot_id"])
    op.create_index(
        "ix_cid_subscriptions_enterprise_override_id",
        "cid_subscriptions",
        ["enterprise_override_id"],
    )
    op.create_index("ix_cid_subscriptions_next_renewal_at", "cid_subscriptions", ["next_renewal_at"])
    op.create_index("ix_cid_subscriptions_created_at", "cid_subscriptions", ["created_at"])

    # 3. plan_snapshots
    op.create_table(
        "plan_snapshots",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("plan_key", sa.String(30), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("price_amount", sa.Float(), nullable=True),
        sa.Column("price_currency", sa.String(10), nullable=False, server_default="EUR"),
        sa.Column("billing_cycle", sa.String(20), nullable=False),
        sa.Column("credits_included_per_period", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("users_included", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("projects_active_max", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("storage_gb", sa.Float(), nullable=False, server_default="0"),
        sa.Column("concurrent_ai_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("modules_included_json", sa.JSON(), nullable=True),
        sa.Column("modules_limited_quotas_json", sa.JSON(), nullable=True),
        sa.Column("exports_per_period", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("support_tier", sa.String(50), nullable=True),
        sa.Column("audit_retention_days", sa.Integer(), nullable=True),
        sa.Column("data_retention_days_after_cancellation", sa.Integer(), nullable=True),
        sa.Column("ai_traceability_level", sa.String(30), nullable=True),
        sa.Column("canon_version", sa.String(50), nullable=False),
        sa.Column("effective_from", sa.DateTime(), nullable=False),
        sa.Column("effective_to", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_plan_snapshots_plan_key",
        ),
        sa.CheckConstraint(
            _enum_ck("billing_cycle", BILLING_CYCLES),
            name="ck_plan_snapshots_billing_cycle",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_plan_snapshots_effective_to_after_from",
        ),
    )
    op.create_index("ix_plan_snapshots_plan_key", "plan_snapshots", ["plan_key"])
    op.create_index("ix_plan_snapshots_billing_cycle", "plan_snapshots", ["billing_cycle"])
    op.create_index("ix_plan_snapshots_canon_version", "plan_snapshots", ["canon_version"])
    op.create_index("ix_plan_snapshots_effective_from", "plan_snapshots", ["effective_from"])

    # 4. plan_change_history
    op.create_table(
        "plan_change_history",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("subscription_id", sa.String(36), nullable=False),
        sa.Column("from_plan_snapshot_id", sa.String(36), nullable=True),
        sa.Column("to_plan_snapshot_id", sa.String(36), nullable=False),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column("effective_at", sa.DateTime(), nullable=False),
        sa.Column("pro_rata_amount_eur", sa.Float(), nullable=True),
        sa.Column("credit_balance_carried_eur", sa.Float(), nullable=True),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_plan_change_history_subscription_id", "plan_change_history", ["subscription_id"]
    )
    op.create_index(
        "ix_plan_change_history_from_plan_snapshot_id",
        "plan_change_history",
        ["from_plan_snapshot_id"],
    )
    op.create_index(
        "ix_plan_change_history_to_snapshot", "plan_change_history", ["to_plan_snapshot_id"]
    )
    op.create_index("ix_plan_change_history_actor_id", "plan_change_history", ["actor_id"])
    op.create_index("ix_plan_change_history_effective_at", "plan_change_history", ["effective_at"])
    op.create_index("ix_plan_change_history_created_at", "plan_change_history", ["created_at"])

    # 5. credit_balances
    op.create_table(
        "credit_balances",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("included_monthly_remaining", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("purchased_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("promotional_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trial_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enterprise_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved_active", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_period", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expired_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("refunded_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("adjusted_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_period_start", sa.DateTime(), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint(
            "included_monthly_remaining >= 0 AND purchased_balance >= 0 AND "
            "promotional_balance >= 0 AND trial_balance >= 0 AND "
            "enterprise_balance >= 0 AND reserved_active >= 0",
            name="ck_credit_balances_non_negative_subbalances",
        ),
        sa.UniqueConstraint("organization_id", name="uq_credit_balances_organization_id"),
    )
    op.create_index("ix_credit_balances_organization_id", "credit_balances", ["organization_id"])
    op.create_index("ix_credit_balances_last_updated_at", "credit_balances", ["last_updated_at"])

    # 6. credit_ledger_entries
    op.create_table(
        "credit_ledger_entries",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=True),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("job_id", sa.String(36), nullable=True),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("credit_package_purchase_id", sa.String(36), nullable=True),
        sa.Column("entry_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=True),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("reserved_until", sa.DateTime(), nullable=True),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("entry_type", CREDIT_LEDGER_ENTRY_TYPES),
            name="ck_credit_ledger_entries_entry_type",
        ),
        sa.CheckConstraint(
            _enum_ck("status", CREDIT_ENTRY_STATUSES),
            name="ck_credit_ledger_entries_status",
        ),
        sa.CheckConstraint("amount <> 0", name="ck_credit_ledger_entries_amount_nonzero"),
        sa.UniqueConstraint("idempotency_key", name="uq_credit_ledger_entries_idempotency_key"),
    )
    op.create_index(
        "ix_credit_ledger_entries_organization_id", "credit_ledger_entries", ["organization_id"]
    )
    op.create_index("ix_credit_ledger_entries_project_id", "credit_ledger_entries", ["project_id"])
    op.create_index("ix_credit_ledger_entries_user_id", "credit_ledger_entries", ["user_id"])
    op.create_index("ix_credit_ledger_entries_job_id", "credit_ledger_entries", ["job_id"])
    op.create_index(
        "ix_credit_ledger_entries_subscription_id", "credit_ledger_entries", ["subscription_id"]
    )
    op.create_index(
        "ix_credit_ledger_entries_package_purchase_id",
        "credit_ledger_entries",
        ["credit_package_purchase_id"],
    )
    op.create_index("ix_credit_ledger_entries_entry_type", "credit_ledger_entries", ["entry_type"])
    op.create_index("ix_credit_ledger_entries_status", "credit_ledger_entries", ["status"])
    op.create_index("ix_credit_ledger_entries_idempotency_key", "credit_ledger_entries", ["idempotency_key"])
    op.create_index("ix_credit_ledger_entries_created_at", "credit_ledger_entries", ["created_at"])

    # 7. credit_package_purchases
    op.create_table(
        "credit_package_purchases",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("billing_account_id", sa.String(36), nullable=False),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("package_key", sa.String(80), nullable=False),
        sa.Column("compatible_plan_key", sa.String(30), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column("price_amount", sa.Float(), nullable=True),
        sa.Column("price_currency", sa.String(10), nullable=False, server_default="EUR"),
        sa.Column("purchased_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("provider_reference_id", sa.String(36), nullable=True),
        sa.Column("invoice_reference_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            _enum_ck("compatible_plan_key", BILLING_PLAN_KEYS),
            name="ck_credit_package_purchases_compatible_plan_key",
        ),
        sa.CheckConstraint(
            _enum_ck("status", CREDIT_PACKAGE_PURCHASE_STATUSES),
            name="ck_credit_package_purchases_status",
        ),
        sa.CheckConstraint("credits > 0", name="ck_credit_package_purchases_credits_positive"),
    )
    op.create_index(
        "ix_credit_package_purchases_organization_id",
        "credit_package_purchases",
        ["organization_id"],
    )
    op.create_index(
        "ix_credit_package_purchases_billing_account_id",
        "credit_package_purchases",
        ["billing_account_id"],
    )
    op.create_index(
        "ix_credit_package_purchases_subscription_id",
        "credit_package_purchases",
        ["subscription_id"],
    )
    op.create_index("ix_credit_package_purchases_package_key", "credit_package_purchases", ["package_key"])
    op.create_index(
        "ix_credit_package_purchases_status", "credit_package_purchases", ["status"]
    )
    op.create_index(
        "ix_credit_package_purchases_provider_reference_id",
        "credit_package_purchases",
        ["provider_reference_id"],
    )
    op.create_index(
        "ix_credit_package_purchases_invoice_reference_id",
        "credit_package_purchases",
        ["invoice_reference_id"],
    )
    op.create_index("ix_credit_package_purchases_expires_at", "credit_package_purchases", ["expires_at"])

    # 8. invoice_references
    op.create_table(
        "invoice_references",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("billing_account_id", sa.String(36), nullable=False),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("provider_reference_id", sa.String(36), nullable=True),
        sa.Column("provider_type", sa.String(30), nullable=False, server_default="stripe"),
        sa.Column("provider_invoice_id", sa.String(255), nullable=True),
        sa.Column("invoice_number", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="EUR"),
        sa.Column("amount_subtotal", sa.Float(), nullable=True),
        sa.Column("amount_tax", sa.Float(), nullable=True),
        sa.Column("amount_total", sa.Float(), nullable=True),
        sa.Column("tax_country", sa.String(2), nullable=True),
        sa.Column("pdf_url", sa.String(1000), nullable=True),
        sa.Column("hosted_invoice_url", sa.String(1000), nullable=True),
        sa.Column("issued_at", sa.DateTime(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("failed_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("provider_type", PAYMENT_PROVIDER_TYPES),
            name="ck_invoice_references_provider_type",
        ),
        sa.CheckConstraint(
            _enum_ck("status", INVOICE_STATUSES),
            name="ck_invoice_references_status",
        ),
    )
    op.create_index("ix_invoice_references_billing_account_id", "invoice_references", ["billing_account_id"])
    op.create_index("ix_invoice_references_subscription_id", "invoice_references", ["subscription_id"])
    op.create_index(
        "ix_invoice_references_provider_reference_id",
        "invoice_references",
        ["provider_reference_id"],
    )
    op.create_index(
        "ix_invoice_references_provider_invoice_id", "invoice_references", ["provider_invoice_id"]
    )
    op.create_index("ix_invoice_references_status", "invoice_references", ["status"])
    op.create_index("ix_invoice_references_issued_at", "invoice_references", ["issued_at"])
    op.create_index("ix_invoice_references_paid_at", "invoice_references", ["paid_at"])
    op.create_index("ix_invoice_references_created_at", "invoice_references", ["created_at"])

    # 9. payment_provider_references
    op.create_table(
        "payment_provider_references",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("billing_account_id", sa.String(36), nullable=False),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("provider_type", sa.String(30), nullable=False, server_default="stripe"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("stripe_price_id", sa.String(255), nullable=True),
        sa.Column("stripe_product_id", sa.String(255), nullable=True),
        sa.Column("stripe_invoice_id", sa.String(255), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(255), nullable=True),
        sa.Column("provider_event_id", sa.String(255), nullable=True),
        sa.Column("provider_event_hash", sa.String(255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("provider_type", PAYMENT_PROVIDER_TYPES),
            name="ck_payment_provider_references_provider_type",
        ),
        sa.UniqueConstraint(
            "provider_event_id", name="uq_payment_provider_references_provider_event_id"
        ),
    )
    op.create_index(
        "ix_payment_provider_references_billing_account_id",
        "payment_provider_references",
        ["billing_account_id"],
    )
    op.create_index(
        "ix_payment_provider_references_subscription_id",
        "payment_provider_references",
        ["subscription_id"],
    )
    op.create_index(
        "ix_payment_provider_references_provider_type",
        "payment_provider_references",
        ["provider_type"],
    )
    op.create_index(
        "ix_payment_provider_references_stripe_customer_id",
        "payment_provider_references",
        ["stripe_customer_id"],
    )
    op.create_index(
        "ix_payment_provider_references_stripe_subscription_id",
        "payment_provider_references",
        ["stripe_subscription_id"],
    )
    op.create_index(
        "ix_payment_provider_references_provider_event_id",
        "payment_provider_references",
        ["provider_event_id"],
    )
    op.create_index(
        "ix_payment_provider_references_last_synced_at",
        "payment_provider_references",
        ["last_synced_at"],
    )
    op.create_index(
        "ix_payment_provider_references_updated_at",
        "payment_provider_references",
        ["updated_at"],
    )

    # 10. enterprise_overrides
    op.create_table(
        "enterprise_overrides",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("billing_account_id", sa.String(36), nullable=True),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("override_type", sa.String(50), nullable=False),
        sa.Column("override_value_json", sa.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("approved_by_user_id", sa.String(36), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("override_type", ENTERPRISE_OVERRIDE_TYPES),
            name="ck_enterprise_overrides_override_type",
        ),
        sa.CheckConstraint(
            "ends_at IS NULL OR ends_at >= starts_at",
            name="ck_enterprise_overrides_ends_at_after_starts_at",
        ),
    )
    op.create_index(
        "ix_enterprise_overrides_organization_id", "enterprise_overrides", ["organization_id"]
    )
    op.create_index(
        "ix_enterprise_overrides_billing_account_id",
        "enterprise_overrides",
        ["billing_account_id"],
    )
    op.create_index(
        "ix_enterprise_overrides_subscription_id", "enterprise_overrides", ["subscription_id"]
    )
    op.create_index("ix_enterprise_overrides_override_type", "enterprise_overrides", ["override_type"])
    op.create_index("ix_enterprise_overrides_active", "enterprise_overrides", ["active"])
    op.create_index(
        "ix_enterprise_overrides_approved_by_user_id",
        "enterprise_overrides",
        ["approved_by_user_id"],
    )
    op.create_index("ix_enterprise_overrides_starts_at", "enterprise_overrides", ["starts_at"])
    op.create_index("ix_enterprise_overrides_ends_at", "enterprise_overrides", ["ends_at"])

    # 11. billing_events
    op.create_table(
        "billing_events",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("billing_account_id", sa.String(36), nullable=True),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("from_status", sa.String(30), nullable=True),
        sa.Column("to_status", sa.String(30), nullable=True),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("provider_event_id", sa.String(255), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("event_type", BILLING_EVENT_TYPES),
            name="ck_billing_events_event_type",
        ),
    )
    op.create_index("ix_billing_events_organization_id", "billing_events", ["organization_id"])
    op.create_index("ix_billing_events_billing_account_id", "billing_events", ["billing_account_id"])
    op.create_index("ix_billing_events_subscription_id", "billing_events", ["subscription_id"])
    op.create_index("ix_billing_events_event_type", "billing_events", ["event_type"])
    op.create_index("ix_billing_events_actor_id", "billing_events", ["actor_id"])
    op.create_index("ix_billing_events_provider_event_id", "billing_events", ["provider_event_id"])
    op.create_index("ix_billing_events_created_at", "billing_events", ["created_at"])

    # 12. trial_entitlements
    op.create_table(
        "trial_entitlements",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("plan_key", sa.String(30), nullable=False, server_default="pro"),
        sa.Column("trial_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("requires_card", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_trial_entitlements_plan_key",
        ),
        sa.CheckConstraint(
            _enum_ck("status", COMMERCIAL_ENTITLEMENT_STATUSES),
            name="ck_trial_entitlements_status",
        ),
        sa.CheckConstraint("ends_at >= starts_at", name="ck_trial_entitlements_ends_at_after_starts_at"),
    )
    op.create_index("ix_trial_entitlements_organization_id", "trial_entitlements", ["organization_id"])
    op.create_index("ix_trial_entitlements_subscription_id", "trial_entitlements", ["subscription_id"])
    op.create_index("ix_trial_entitlements_status", "trial_entitlements", ["status"])
    op.create_index("ix_trial_entitlements_ends_at", "trial_entitlements", ["ends_at"])

    # 13. demo_entitlements
    op.create_table(
        "demo_entitlements",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("granted_by_user_id", sa.String(36), nullable=True),
        sa.Column("plan_key", sa.String(30), nullable=True),
        sa.Column("manual_limits_json", sa.JSON(), nullable=True),
        sa.Column("demo_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("conversion_target_plan", sa.String(30), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("status", COMMERCIAL_ENTITLEMENT_STATUSES),
            name="ck_demo_entitlements_status",
        ),
        sa.CheckConstraint(
            "(plan_key IS NULL) OR ({})".format(_enum_ck("plan_key", BILLING_PLAN_KEYS)),
            name="ck_demo_entitlements_plan_key",
        ),
        sa.CheckConstraint(
            "(conversion_target_plan IS NULL) OR ({})".format(
                _enum_ck("conversion_target_plan", BILLING_PLAN_KEYS)
            ),
            name="ck_demo_entitlements_conversion_target_plan",
        ),
    )
    op.create_index("ix_demo_entitlements_organization_id", "demo_entitlements", ["organization_id"])
    op.create_index(
        "ix_demo_entitlements_granted_by_user_id", "demo_entitlements", ["granted_by_user_id"]
    )
    op.create_index("ix_demo_entitlements_status", "demo_entitlements", ["status"])
    op.create_index("ix_demo_entitlements_ends_at", "demo_entitlements", ["ends_at"])

    # 14. beta_entitlements
    op.create_table(
        "beta_entitlements",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("beta_program_key", sa.String(80), nullable=False),
        sa.Column("feedback_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("plan_key", sa.String(30), nullable=False, server_default="pro"),
        sa.Column("beta_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("converted_subscription_id", sa.String(36), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            _enum_ck("plan_key", BILLING_PLAN_KEYS),
            name="ck_beta_entitlements_plan_key",
        ),
        sa.CheckConstraint(
            _enum_ck("status", COMMERCIAL_ENTITLEMENT_STATUSES),
            name="ck_beta_entitlements_status",
        ),
        sa.CheckConstraint("ends_at >= starts_at", name="ck_beta_entitlements_ends_at_after_starts_at"),
    )
    op.create_index("ix_beta_entitlements_organization_id", "beta_entitlements", ["organization_id"])
    op.create_index(
        "ix_beta_entitlements_beta_program_key", "beta_entitlements", ["beta_program_key"]
    )
    op.create_index("ix_beta_entitlements_status", "beta_entitlements", ["status"])
    op.create_index("ix_beta_entitlements_ends_at", "beta_entitlements", ["ends_at"])
    op.create_index(
        "ix_beta_entitlements_converted_subscription_id",
        "beta_entitlements",
        ["converted_subscription_id"],
    )


def downgrade() -> None:
    # Drop in reverse order to keep table dependency graph consistent.
    op.drop_table("beta_entitlements")
    op.drop_table("demo_entitlements")
    op.drop_table("trial_entitlements")
    op.drop_table("billing_events")
    op.drop_table("enterprise_overrides")
    op.drop_table("payment_provider_references")
    op.drop_table("invoice_references")
    op.drop_table("credit_package_purchases")
    op.drop_table("credit_ledger_entries")
    op.drop_table("credit_balances")
    op.drop_table("plan_change_history")
    op.drop_table("plan_snapshots")
    op.drop_table("cid_subscriptions")
    op.drop_table("billing_accounts")
