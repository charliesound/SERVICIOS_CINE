#!/usr/bin/env python3
"""
Internal CLI for per-tenant reconciliation of cancelled AI job credit releases.

Usage:
    python scripts/ops/reconcile_cancelled_ai_job_credit_releases.py \
        --organization-id <id> \
        [--max-items 50] \
        [--dry-run] \
        [--requested-by "ops-user"] \
        [--json]

Requires DATABASE_URL env var to be set (postgresql+asyncpg://).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

logger = logging.getLogger("reconcile_cancelled_ai_job_credit_releases")

EXIT_SUCCESS = 0
EXIT_PARTIAL_FAILURE = 1
EXIT_BAD_ARGS = 2
EXIT_UNEXPECTED_ERROR = 3


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconcile cancelled AI job credit releases per tenant.",
    )
    parser.add_argument(
        "--organization-id",
        required=True,
        help="Tenant organization ID (required).",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=50,
        help="Maximum jobs to process per run (default: 50, capped at 100).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Inspect eligible jobs without performing releases.",
    )
    parser.add_argument(
        "--requested-by",
        default="ops-cli",
        help="Operator identifier for audit trail (default: ops-cli).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output structured JSON instead of human-readable summary.",
    )
    args = parser.parse_args(argv)

    if args.max_items < 1:
        parser.error("--max-items must be >= 1")

    return args


def _build_result_dict(
    result: object,
    *,
    duration_seconds: float,
    dry_run: bool,
) -> dict[str, Any]:
    per_job = []
    raw_results = getattr(result, "per_job_results", [])
    for item in raw_results:
        per_job.append(
            {
                "job_id": str(getattr(item, "job_id", "") or ""),
                "organization_id": str(getattr(item, "organization_id", "") or ""),
                "error_category": str(getattr(item, "error_category", "") or ""),
                "release_entry_id": (
                    str(getattr(item, "release_entry_id", "") or "")
                    if getattr(item, "release_entry_id", None) is not None
                    else None
                ),
                "release_performed": bool(getattr(item, "release_performed", False)),
                "idempotent": bool(getattr(item, "idempotent", False)),
                "status_before": (
                    str(getattr(item, "status_before", "") or "")
                    if getattr(item, "status_before", None) is not None
                    else None
                ),
                "status_after": (
                    str(getattr(item, "status_after", "") or "")
                    if getattr(item, "status_after", None) is not None
                    else None
                ),
                "message": str(getattr(item, "message", "") or ""),
            }
        )

    return {
        "organization_id": getattr(result, "organization_id", "") or "",
        "dry_run": dry_run,
        "scanned_count": getattr(result, "scanned_count", 0) or 0,
        "processed_count": getattr(result, "processed_count", 0) or 0,
        "released_count": getattr(result, "released_count", 0) or 0,
        "skipped_count": getattr(result, "skipped_count", 0) or 0,
        "failed_count": getattr(result, "failed_count", 0) or 0,
        "duration_seconds": round(duration_seconds, 3),
        "per_job_results": per_job,
    }


def _print_human(result: object, *, duration_seconds: float, dry_run: bool) -> None:
    data = _build_result_dict(result, duration_seconds=duration_seconds, dry_run=dry_run)
    print("--- Cancel Credit Release Reconciliation ---")
    print(f"  Organization ID : {data['organization_id']}")
    print(f"  Dry Run         : {data['dry_run']}")
    print(f"  Duration        : {data['duration_seconds']}s")
    print(f"  Scanned         : {data['scanned_count']}")
    print(f"  Processed       : {data['processed_count']}")
    print(f"  Released        : {data['released_count']}")
    print(f"  Skipped         : {data['skipped_count']}")
    print(f"  Failed          : {data['failed_count']}")
    if data["per_job_results"]:
        print(f"  Jobs:")
        for job in data["per_job_results"]:
            print(
                f"    {job['job_id']}: "
                f"cat={job['error_category']} "
                f"release_id={job['release_entry_id'] or 'N/A'} "
                f"performed={job['release_performed']} "
                f"idempotent={job['idempotent']}"
            )


def _print_json(result: object, *, duration_seconds: float, dry_run: bool) -> None:
    data = _build_result_dict(result, duration_seconds=duration_seconds, dry_run=dry_run)
    print(json.dumps(data, indent=2, default=str))


async def run_reconciliation(
    args: argparse.Namespace,
) -> Any:
    from database import AsyncSessionLocal
    from repositories.ai_job_repository import AIJobRepository
    from services.ai_job_accounting_gateway import AIJobAccountingGateway
    from services.ai_job_async_orchestration_service import (
        AIJobAsyncCancelCreditReleaseReconciliationRequest,
        AIJobAsyncOrchestrationService,
    )
    from services.ai_job_costing_service import AIJobCostingService

    async with AsyncSessionLocal() as session:
        repository = AIJobRepository(session)
        accounting_gateway = AIJobAccountingGateway(AIJobCostingService())
        service = AIJobAsyncOrchestrationService(
            repository=repository,
            accounting_gateway=accounting_gateway,
        )

        request = AIJobAsyncCancelCreditReleaseReconciliationRequest(
            organization_id=args.organization_id,
            max_items=args.max_items,
            dry_run=args.dry_run,
            requested_by=args.requested_by,
        )

        result = await service.process_cancelled_ai_job_credit_releases(session, request)
        await session.commit()
        return result


async def main_async(args: argparse.Namespace) -> int:
    try:
        start = time.monotonic()
        result = await run_reconciliation(args)
        duration = time.monotonic() - start

        failed_count = getattr(result, "failed_count", 0) or 0

        if args.json:
            _print_json(result, duration_seconds=duration, dry_run=args.dry_run)
        else:
            _print_human(result, duration_seconds=duration, dry_run=args.dry_run)

        if failed_count > 0:
            return EXIT_PARTIAL_FAILURE
        return EXIT_SUCCESS

    except Exception as exc:
        logger.error("Unexpected error during reconciliation: %s", exc)
        if args.json:
            print(json.dumps({"error": str(exc), "error_type": exc.__class__.__name__}))
        else:
            print(f"ERROR: {exc}")
        return EXIT_UNEXPECTED_ERROR


def main() -> None:
    try:
        args = parse_args()
    except SystemExit as exc:
        sys.exit(exc.code)
    except Exception as exc:
        print(f"ERROR: argument parsing failed: {exc}")
        sys.exit(EXIT_BAD_ARGS)

    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
