from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


CREDIT_GRANT_BUCKETS = (
    "trial_balance",
    "promotional_balance",
    "included_monthly_remaining",
    "purchased_balance",
    "enterprise_balance",
)


class CreditAvailabilityRead(BaseModel):
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    status: str = ""
    message: str = ""

    model_config = ConfigDict(from_attributes=True)


class CreditGrantRequest(BaseModel):
    organization_id: str
    amount: int = Field(gt=0)
    bucket: str = "promotional_balance"
    reason: Optional[str] = None
    metadata: dict[str, Any] | None = None
    idempotency_key: Optional[str] = None


class CreditReserveRequest(BaseModel):
    organization_id: str
    amount: int = Field(gt=0)
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    job_id: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict[str, Any] | None = None
    idempotency_key: Optional[str] = None


class CreditReleaseRequest(BaseModel):
    organization_id: str
    amount: int = Field(gt=0)
    job_id: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict[str, Any] | None = None
    idempotency_key: Optional[str] = None


class CreditConsumeRequest(BaseModel):
    organization_id: str
    amount: int = Field(gt=0)
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    job_id: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict[str, Any] | None = None
    idempotency_key: Optional[str] = None


class CreditLedgerOperationResult(BaseModel):
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    ledger_entry_id: Optional[str] = None
    status: str = ""
    message: str = ""
    bucket: Optional[str] = None
    bucket_debits: dict[str, int] | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "CREDIT_GRANT_BUCKETS",
    "CreditAvailabilityRead",
    "CreditGrantRequest",
    "CreditReserveRequest",
    "CreditReleaseRequest",
    "CreditConsumeRequest",
    "CreditLedgerOperationResult",
]
