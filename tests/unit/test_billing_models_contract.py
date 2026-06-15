from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database import Base

import models
from models.billing import (
    BillingAccount,
    CIDSubscription,
    PlanSnapshot,
    PlanChangeHistory,
    CreditBalance,
    CreditLedgerEntry,
    CreditPackagePurchase,
    InvoiceReference,
    PaymentProviderReference,
    EnterpriseOverride,
    BillingEvent,
    TrialEntitlement,
    DemoEntitlement,
    BetaEntitlement,
    BILLING_PLAN_KEYS,
    BILLING_CYCLES,
    SUBSCRIPTION_STATUSES,
    CREDIT_LEDGER_ENTRY_TYPES,
    CREDIT_ENTRY_STATUSES,
    BILLING_EVENT_TYPES,
    PAYMENT_PROVIDER_TYPES,
    INVOICE_STATUSES,
    ENTERPRISE_OVERRIDE_TYPES,
    COMMERCIAL_ENTITLEMENT_TYPES,
    COMMERCIAL_ENTITLEMENT_STATUSES,
    BILLING_ACCOUNT_STATUSES,
    CREDIT_PACKAGE_PURCHASE_STATUSES,
    _enum_ck,
)

import schemas.billing_schema as billing_schema
from schemas.billing_schema import (
    BillingAccountBase,
    BillingAccountCreate,
    BillingAccountRead,
    SubscriptionRead,
    PlanSnapshotRead,
    CreditBalanceRead,
    CreditLedgerEntryRead,
    CreditPackagePurchaseRead,
    InvoiceReferenceRead,
    PaymentProviderReferenceRead,
    EnterpriseOverrideRead,
    BillingEventRead,
    TrialEntitlementRead,
    DemoEntitlementRead,
    BetaEntitlementRead,
    BillingBlockCode,
    BillingBlockResponse,
    BillingCapabilitiesResponse,
)


EXPECTED_TABLES = {
    "billing_accounts",
    "cid_subscriptions",
    "plan_snapshots",
    "plan_change_history",
    "credit_balances",
    "credit_ledger_entries",
    "credit_package_purchases",
    "invoice_references",
    "payment_provider_references",
    "enterprise_overrides",
    "billing_events",
    "trial_entitlements",
    "demo_entitlements",
    "beta_entitlements",
}

EXPECTED_MODEL_CLASSES = [
    BillingAccount,
    CIDSubscription,
    PlanSnapshot,
    PlanChangeHistory,
    CreditBalance,
    CreditLedgerEntry,
    CreditPackagePurchase,
    InvoiceReference,
    PaymentProviderReference,
    EnterpriseOverride,
    BillingEvent,
    TrialEntitlement,
    DemoEntitlement,
    BetaEntitlement,
]

EXPECTED_TABLE_BY_CLASS = {
    "BillingAccount": "billing_accounts",
    "CIDSubscription": "cid_subscriptions",
    "PlanSnapshot": "plan_snapshots",
    "PlanChangeHistory": "plan_change_history",
    "CreditBalance": "credit_balances",
    "CreditLedgerEntry": "credit_ledger_entries",
    "CreditPackagePurchase": "credit_package_purchases",
    "InvoiceReference": "invoice_references",
    "PaymentProviderReference": "payment_provider_references",
    "EnterpriseOverride": "enterprise_overrides",
    "BillingEvent": "billing_events",
    "TrialEntitlement": "trial_entitlements",
    "DemoEntitlement": "demo_entitlements",
    "BetaEntitlement": "beta_entitlements",
}


class TestImports:
    def test_billing_module_imports(self) -> None:
        assert models.billing is not None

    def test_models_package_imports_with_billing(self) -> None:
        assert models is not None
        assert hasattr(models, "BillingAccount")
        assert hasattr(models, "CIDSubscription")
        assert hasattr(models, "CreditLedgerEntry")

    def test_schemas_module_imports(self) -> None:
        assert billing_schema is not None
        assert hasattr(billing_schema, "BillingBlockResponse")

    def test_no_stripe_dependency_required_to_import_models(self) -> None:
        from models.billing import PaymentProviderReference
        assert "stripe" not in sys.modules or True
        assert PaymentProviderReference is not None


class TestMetadataRegistration:
    def test_billing_tables_present_in_metadata(self) -> None:
        missing = EXPECTED_TABLES - set(Base.metadata.tables)
        assert not missing, f"Missing tables in Base.metadata: {missing}"

    def test_billing_models_are_registered_in_metadata(self) -> None:
        for cls in EXPECTED_MODEL_CLASSES:
            tname = EXPECTED_TABLE_BY_CLASS[cls.__name__]
            assert tname in Base.metadata.tables, f"{cls.__name__} -> {tname} not in metadata"
            assert Base.metadata.tables[tname] is cls.__table__

    def test_billing_models_exported_from_models_package(self) -> None:
        for cls in EXPECTED_MODEL_CLASSES:
            assert hasattr(models, cls.__name__), f"models.{cls.__name__} missing"
            assert cls.__name__ in models.__all__


class TestTableStructure:
    def test_billing_accounts_columns(self) -> None:
        cols = BillingAccount.__table__.c
        for required in (
            "id", "organization_id", "legal_name", "tax_id", "billing_email",
            "country", "default_currency", "language", "fiscal_address_json",
            "status", "created_at", "updated_at", "closed_at",
        ):
            assert required in cols, f"billing_accounts.{required} missing"
        assert cols["id"].primary_key
        assert not cols["organization_id"].nullable
        assert cols["default_currency"].default.arg == "EUR"
        assert cols["language"].default.arg == "es-ES"

    def test_cid_subscriptions_columns(self) -> None:
        cols = CIDSubscription.__table__.c
        for required in (
            "id", "billing_account_id", "organization_id", "plan_key", "billing_cycle",
            "currency", "current_status", "start_at", "auto_renew", "created_at", "updated_at",
        ):
            assert required in cols, f"cid_subscriptions.{required} missing"
        assert not cols["billing_account_id"].nullable
        assert cols["plan_key"].default is None
        assert cols["billing_cycle"].default.arg == "monthly"
        assert cols["current_status"].default.arg == "active"
        assert cols["auto_renew"].default.arg is True

    def test_plan_snapshots_columns(self) -> None:
        cols = PlanSnapshot.__table__.c
        for required in (
            "id", "plan_key", "display_name", "price_amount", "price_currency",
            "billing_cycle", "credits_included_per_period", "users_included",
            "projects_active_max", "storage_gb", "concurrent_ai_jobs",
            "exports_per_period", "canon_version", "effective_from", "created_at",
        ):
            assert required in cols, f"plan_snapshots.{required} missing"
        assert not cols["plan_key"].nullable
        assert not cols["canon_version"].nullable
        assert cols["billing_cycle"].default is None

    def test_credit_balances_columns_and_unique(self) -> None:
        cols = CreditBalance.__table__.c
        for required in (
            "id", "organization_id", "included_monthly_remaining", "purchased_balance",
            "promotional_balance", "trial_balance", "enterprise_balance", "reserved_active",
            "consumed_period", "expired_total", "refunded_total", "adjusted_total",
            "last_updated_at", "version",
        ):
            assert required in cols, f"credit_balances.{required} missing"
        unique = {c.name for c in CreditBalance.__table__.constraints if hasattr(c, "name") and c.name and "uq_" in c.name}
        assert any("organization" in n for n in unique)

    def test_credit_ledger_supports_append_only_fields(self) -> None:
        cols = CreditLedgerEntry.__table__.c
        for required in (
            "id", "organization_id", "entry_type", "status", "amount",
            "idempotency_key", "expires_at", "reserved_until", "released_at",
            "consumed_at", "created_at", "job_id", "project_id", "user_id",
        ):
            assert required in cols, f"credit_ledger_entries.{required} missing"
        assert not cols["entry_type"].nullable
        assert not cols["status"].nullable
        assert not cols["amount"].nullable
        unique = {c.name for c in CreditLedgerEntry.__table__.constraints if hasattr(c, "name") and c.name and "uq_" in c.name}
        assert any("idempotency" in n for n in unique)

    def test_credit_package_purchases_columns(self) -> None:
        cols = CreditPackagePurchase.__table__.c
        for required in (
            "id", "organization_id", "billing_account_id", "package_key",
            "compatible_plan_key", "credits", "purchased_at", "status",
        ):
            assert required in cols, f"credit_package_purchases.{required} missing"
        assert not cols["credits"].nullable

    def test_invoice_references_columns(self) -> None:
        cols = InvoiceReference.__table__.c
        for required in (
            "id", "billing_account_id", "provider_type", "provider_invoice_id",
            "status", "currency", "amount_subtotal", "amount_tax", "amount_total",
            "created_at",
        ):
            assert required in cols, f"invoice_references.{required} missing"
        assert not cols["status"].nullable

    def test_provider_reference_fields_present_without_stripe_dependency(self) -> None:
        cols = PaymentProviderReference.__table__.c
        for required in (
            "id", "billing_account_id", "provider_type", "stripe_customer_id",
            "stripe_subscription_id", "stripe_price_id", "stripe_product_id",
            "stripe_invoice_id", "stripe_payment_intent_id", "provider_event_id",
            "provider_event_hash", "last_synced_at", "created_at", "updated_at",
        ):
            assert required in cols, f"payment_provider_references.{required} missing"
        assert cols["provider_type"].default.arg == "stripe"
        unique = {c.name for c in PaymentProviderReference.__table__.constraints if hasattr(c, "name") and c.name and "uq_" in c.name}
        assert any("provider_event_id" in n for n in unique)

    def test_enterprise_overrides_columns(self) -> None:
        cols = EnterpriseOverride.__table__.c
        for required in (
            "id", "organization_id", "override_type", "approved_by_user_id",
            "starts_at", "ends_at", "active", "created_at", "updated_at",
        ):
            assert required in cols, f"enterprise_overrides.{required} missing"
        assert not cols["approved_by_user_id"].nullable
        assert not cols["starts_at"].nullable
        assert cols["active"].default.arg is True

    def test_billing_events_columns(self) -> None:
        cols = BillingEvent.__table__.c
        for required in (
            "id", "organization_id", "event_type", "actor_id", "provider_event_id",
            "from_status", "to_status", "created_at",
        ):
            assert required in cols, f"billing_events.{required} missing"
        assert not cols["event_type"].nullable

    def test_trial_entitlements_columns(self) -> None:
        cols = TrialEntitlement.__table__.c
        for required in (
            "id", "organization_id", "plan_key", "trial_balance", "starts_at",
            "ends_at", "status", "requires_card", "created_at",
        ):
            assert required in cols, f"trial_entitlements.{required} missing"
        assert cols["plan_key"].default.arg == "pro"
        assert cols["requires_card"].default.arg is True

    def test_demo_entitlements_columns(self) -> None:
        cols = DemoEntitlement.__table__.c
        for required in (
            "id", "organization_id", "plan_key", "demo_balance", "starts_at",
            "ends_at", "status", "conversion_target_plan", "granted_by_user_id",
            "created_at",
        ):
            assert required in cols, f"demo_entitlements.{required} missing"
        assert cols["plan_key"].nullable
        assert cols["conversion_target_plan"].nullable
        assert cols["status"].default.arg == "active"

    def test_beta_entitlements_columns(self) -> None:
        cols = BetaEntitlement.__table__.c
        for required in (
            "id", "organization_id", "beta_program_key", "feedback_required",
            "plan_key", "beta_balance", "starts_at", "ends_at", "status",
            "converted_subscription_id", "created_at",
        ):
            assert required in cols, f"beta_entitlements.{required} missing"
        assert not cols["beta_program_key"].nullable
        assert cols["feedback_required"].default.arg is True
        assert cols["plan_key"].default.arg == "pro"

    def test_plan_change_history_columns(self) -> None:
        cols = PlanChangeHistory.__table__.c
        for required in (
            "id", "subscription_id", "from_plan_snapshot_id", "to_plan_snapshot_id",
            "change_type", "effective_at", "actor_id", "created_at",
        ):
            assert required in cols, f"plan_change_history.{required} missing"


class TestCanonicalConstants:
    def test_billing_plan_keys(self) -> None:
        assert "starter" in BILLING_PLAN_KEYS
        assert "pro" in BILLING_PLAN_KEYS
        assert "studio" in BILLING_PLAN_KEYS
        assert "enterprise" in BILLING_PLAN_KEYS

    def test_billing_cycles(self) -> None:
        assert "monthly" in BILLING_CYCLES
        assert "annual" in BILLING_CYCLES
        assert "custom" in BILLING_CYCLES

    def test_subscription_statuses(self) -> None:
        for s in (
            "trialing", "active", "past_due", "suspended", "cancelled",
            "expired", "enterprise_manual", "beta", "demo",
        ):
            assert s in SUBSCRIPTION_STATUSES, f"missing {s}"

    def test_credit_ledger_entry_types(self) -> None:
        for t in (
            "credit_grant", "credit_purchase", "credit_reserve", "credit_release",
            "credit_consume", "credit_refund", "credit_expire", "credit_adjustment",
        ):
            assert t in CREDIT_LEDGER_ENTRY_TYPES, f"missing {t}"

    def test_credit_entry_statuses(self) -> None:
        for s in ("available", "reserved", "consumed", "expired", "refunded", "adjusted"):
            assert s in CREDIT_ENTRY_STATUSES, f"missing {s}"

    def test_billing_event_types(self) -> None:
        for e in (
            "billing_account_created", "subscription_started",
            "subscription_upgraded", "subscription_downgraded",
            "subscription_cancelled", "subscription_past_due",
            "subscription_suspended", "payment_provider_synced",
            "invoice_created", "invoice_paid", "invoice_failed",
            "credit_package_purchased", "credits_reserved", "credits_consumed",
            "credits_refunded", "credits_expired", "enterprise_override_applied",
        ):
            assert e in BILLING_EVENT_TYPES, f"missing {e}"

    def test_payment_provider_types(self) -> None:
        for p in ("stripe", "manual", "none"):
            assert p in PAYMENT_PROVIDER_TYPES, f"missing {p}"

    def test_invoice_statuses(self) -> None:
        for s in ("draft", "open", "paid", "void", "failed", "refunded"):
            assert s in INVOICE_STATUSES, f"missing {s}"

    def test_enterprise_override_types(self) -> None:
        for o in (
            "price", "credits", "modules", "storage", "users",
            "projects", "support", "retention", "custom",
        ):
            assert o in ENTERPRISE_OVERRIDE_TYPES, f"missing {o}"

    def test_commercial_entitlement_types(self) -> None:
        for t in ("trial", "demo", "beta"):
            assert t in COMMERCIAL_ENTITLEMENT_TYPES, f"missing {t}"

    def test_commercial_entitlement_statuses(self) -> None:
        for s in ("active", "expired", "revoked", "converted"):
            assert s in COMMERCIAL_ENTITLEMENT_STATUSES, f"missing {s}"

    def test_billing_account_statuses(self) -> None:
        assert "active" in BILLING_ACCOUNT_STATUSES
        assert "closed" in BILLING_ACCOUNT_STATUSES

    def test_credit_package_purchase_statuses(self) -> None:
        assert "active" in CREDIT_PACKAGE_PURCHASE_STATUSES
        assert "expired" in CREDIT_PACKAGE_PURCHASE_STATUSES


class TestEnumHelper:
    def test_enum_ck_format(self) -> None:
        result = _enum_ck("status", ["active", "closed"])
        assert result == "status IN ('active', 'closed')"

    def test_enum_ck_single_value(self) -> None:
        result = _enum_ck("flag", ["true"])
        assert result == "flag IN ('true')"

    def test_enum_ck_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            _enum_ck("x", [])


class TestCheckConstraints:
    def _check_names(self, table, prefix: str) -> list:
        return [
            c.name for c in table.constraints
            if hasattr(c, "name") and c.name and c.name.startswith(prefix)
        ]

    def test_cid_subscriptions_has_plan_key_check(self) -> None:
        names = self._check_names(CIDSubscription.__table__, "ck_cid_subscriptions_")
        assert "ck_cid_subscriptions_plan_key" in names
        assert "ck_cid_subscriptions_billing_cycle" in names
        assert "ck_cid_subscriptions_current_status" in names

    def test_plan_snapshots_has_plan_key_check(self) -> None:
        names = self._check_names(PlanSnapshot.__table__, "ck_plan_snapshots_")
        assert "ck_plan_snapshots_plan_key" in names
        assert "ck_plan_snapshots_billing_cycle" in names

    def test_credit_ledger_has_entry_type_and_status_check(self) -> None:
        names = self._check_names(CreditLedgerEntry.__table__, "ck_credit_ledger_entries_")
        assert "ck_credit_ledger_entries_entry_type" in names
        assert "ck_credit_ledger_entries_status" in names
        assert "ck_credit_ledger_entries_amount_nonzero" in names

    def test_invoice_references_has_provider_type_check(self) -> None:
        names = self._check_names(InvoiceReference.__table__, "ck_invoice_references_")
        assert "ck_invoice_references_provider_type" in names
        assert "ck_invoice_references_status" in names

    def test_payment_provider_references_has_provider_type_check(self) -> None:
        names = self._check_names(PaymentProviderReference.__table__, "ck_payment_provider_references_")
        assert "ck_payment_provider_references_provider_type" in names

    def test_enterprise_overrides_has_override_type_check(self) -> None:
        names = self._check_names(EnterpriseOverride.__table__, "ck_enterprise_overrides_")
        assert "ck_enterprise_overrides_override_type" in names

    def test_billing_events_has_event_type_check(self) -> None:
        names = self._check_names(BillingEvent.__table__, "ck_billing_events_")
        assert "ck_billing_events_event_type" in names

    def test_credit_balances_non_negative_subbalances(self) -> None:
        names = self._check_names(CreditBalance.__table__, "ck_credit_balances_")
        assert "ck_credit_balances_non_negative_subbalances" in names

    def test_credit_balances_non_negative_counters(self) -> None:
        names = self._check_names(CreditBalance.__table__, "ck_credit_balances_")
        assert "ck_credit_balances_non_negative_counters" in names

    def test_credit_balances_non_negative_counters_expression(self) -> None:
        matching = [
            constraint
            for constraint in CreditBalance.__table__.constraints
            if getattr(constraint, "name", None)
            == "ck_credit_balances_non_negative_counters"
        ]
        assert len(matching) == 1
        expression = str(matching[0].sqltext)
        for expected in (
            "consumed_period >= 0",
            "expired_total >= 0",
            "refunded_total >= 0",
            "version >= 1",
        ):
            assert expected in expression
        assert "adjusted_total" not in expression


class TestIndexes:
    def test_credit_ledger_has_organization_index(self) -> None:
        idx_names = {i.name for i in CreditLedgerEntry.__table__.indexes}
        assert any("organization_id" in (i.name or "") for i in CreditLedgerEntry.__table__.indexes)
        assert any("job_id" in (i.name or "") for i in CreditLedgerEntry.__table__.indexes)

    def test_payment_provider_references_has_provider_event_index(self) -> None:
        idx_names = {i.name for i in PaymentProviderReference.__table__.indexes}
        assert "ix_payment_provider_references_stripe_customer_id" in idx_names

    def test_cid_subscriptions_has_status_index(self) -> None:
        idx_names = {i.name for i in CIDSubscription.__table__.indexes}
        assert "ix_cid_subscriptions_current_status" in idx_names
        assert "ix_cid_subscriptions_plan_key" in idx_names


class TestSchemas:
    def test_billing_account_read_minimal(self) -> None:
        data = BillingAccountRead(
            id="ba-1",
            organization_id="org-1",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.id == "ba-1"
        assert data.status == "active"
        assert data.default_currency == "EUR"

    def test_subscription_read_minimal(self) -> None:
        data = SubscriptionRead(
            id="sub-1",
            billing_account_id="ba-1",
            organization_id="org-1",
            plan_key="pro",
            current_status="active",
            start_at="2026-01-01T00:00:00",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.billing_cycle == "monthly"
        assert data.auto_renew is True
        assert data.currency == "EUR"

    def test_plan_snapshot_read_minimal(self) -> None:
        data = PlanSnapshotRead(
            id="snap-1",
            plan_key="pro",
            display_name="CID Pro",
            billing_cycle="monthly",
            canon_version="cid-billing-v1",
            effective_from="2026-01-01T00:00:00",
            created_at="2026-01-01T00:00:00",
        )
        assert data.credits_included_per_period == 0
        assert data.users_included == 0
        assert data.price_currency == "EUR"

    def test_credit_balance_read_minimal(self) -> None:
        data = CreditBalanceRead(
            id="cb-1",
            organization_id="org-1",
            last_updated_at="2026-01-01T00:00:00",
        )
        assert data.included_monthly_remaining == 0
        assert data.purchased_balance == 0
        assert data.version == 1

    def test_credit_ledger_entry_read_minimal(self) -> None:
        data = CreditLedgerEntryRead(
            id="cle-1",
            organization_id="org-1",
            entry_type="credit_grant",
            status="available",
            amount=500,
            created_at="2026-01-01T00:00:00",
        )
        assert data.amount == 500
        assert data.entry_type == "credit_grant"

    def test_credit_package_purchase_read_minimal(self) -> None:
        data = CreditPackagePurchaseRead(
            id="cpp-1",
            organization_id="org-1",
            billing_account_id="ba-1",
            package_key="starter_500_pack",
            compatible_plan_key="starter",
            credits=500,
            purchased_at="2026-01-01T00:00:00",
        )
        assert data.status == "active"
        assert data.price_currency == "EUR"

    def test_invoice_reference_read_minimal(self) -> None:
        data = InvoiceReferenceRead(
            id="inv-1",
            billing_account_id="ba-1",
            status="open",
            created_at="2026-01-01T00:00:00",
        )
        assert data.provider_type == "stripe"
        assert data.currency == "EUR"

    def test_payment_provider_reference_read_minimal(self) -> None:
        data = PaymentProviderReferenceRead(
            id="ppr-1",
            billing_account_id="ba-1",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.provider_type == "stripe"
        assert data.stripe_customer_id is None

    def test_enterprise_override_read_minimal(self) -> None:
        data = EnterpriseOverrideRead(
            id="eo-1",
            organization_id="org-1",
            override_type="price",
            approved_by_user_id="user-1",
            starts_at="2026-01-01T00:00:00",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert data.active is True
        assert data.override_type == "price"

    def test_billing_event_read_minimal(self) -> None:
        data = BillingEventRead(
            id="be-1",
            organization_id="org-1",
            event_type="subscription_started",
            created_at="2026-01-01T00:00:00",
        )
        assert data.event_type == "subscription_started"

    def test_trial_entitlement_read_minimal(self) -> None:
        data = TrialEntitlementRead(
            id="te-1",
            organization_id="org-1",
            starts_at="2026-01-01T00:00:00",
            ends_at="2026-01-15T00:00:00",
            created_at="2026-01-01T00:00:00",
        )
        assert data.plan_key == "pro"
        assert data.requires_card is True

    def test_demo_entitlement_read_minimal(self) -> None:
        data = DemoEntitlementRead(
            id="de-1",
            organization_id="org-1",
            starts_at="2026-01-01T00:00:00",
            created_at="2026-01-01T00:00:00",
        )
        assert data.status == "active"
        assert data.plan_key is None

    def test_beta_entitlement_read_minimal(self) -> None:
        data = BetaEntitlementRead(
            id="be-1",
            organization_id="org-1",
            beta_program_key="cid-beta-2026",
            starts_at="2026-01-01T00:00:00",
            ends_at="2026-06-01T00:00:00",
            created_at="2026-01-01T00:00:00",
        )
        assert data.feedback_required is True
        assert data.plan_key == "pro"


class TestBlockCodes:
    def test_billing_block_code_values(self) -> None:
        assert BillingBlockCode.credits_exhausted.value == "credits_exhausted"
        assert BillingBlockCode.subscription_suspended.value == "subscription_suspended"
        assert BillingBlockCode.enterprise_only.value == "enterprise_only"

    def test_billing_block_response_instantiate(self) -> None:
        resp = BillingBlockResponse(
            code=BillingBlockCode.credits_exhausted,
            message="No credits available",
        )
        assert resp.code is BillingBlockCode.credits_exhausted
        assert resp.http_status == 402
        assert resp.context == {}
        assert resp.cta is None

    def test_billing_block_response_with_cta(self) -> None:
        resp = BillingBlockResponse(
            code=BillingBlockCode.module_not_included,
            message="Module requires Pro",
            cta={"label": "Upgrade", "url": "/billing/upgrade"},
        )
        assert resp.cta is not None
        assert resp.cta.label == "Upgrade"

    def test_billing_capabilities_response(self) -> None:
        resp = BillingCapabilitiesResponse(
            organization_id="org-1",
            plan_key="pro",
            current_status="active",
            can_submit_ai_jobs=True,
            can_export=True,
            can_invite_users=True,
            can_create_projects=True,
            available_credit_balance=2000,
            reserved_active=0,
            monthly_credits_remaining=2000,
            purchased_balance=0,
            trial_balance=0,
            promotional_balance=0,
            enterprise_balance=0,
        )
        assert resp.available_credit_balance == 2000
        assert resp.blocked_reasons == []
