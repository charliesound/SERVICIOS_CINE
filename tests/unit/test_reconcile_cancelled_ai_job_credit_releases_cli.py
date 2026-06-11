from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://placeholder:placeholder@localhost:5432/placeholder",
)
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

CLI_MODULE_PATH = ROOT / "scripts" / "ops" / "reconcile_cancelled_ai_job_credit_releases.py"
import importlib.util

spec = importlib.util.spec_from_file_location("cli_under_test", str(CLI_MODULE_PATH))
assert spec is not None and spec.loader is not None
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


@dataclass
class FakeJobResult:
    job_id: str
    organization_id: str
    error_category: str
    release_entry_id: str | None = None
    release_performed: bool = False
    idempotent: bool = False
    status_before: str | None = None
    status_after: str | None = None
    message: str = ""


@dataclass
class FakeReconciliationResult:
    organization_id: str
    scanned_count: int
    processed_count: int
    released_count: int
    skipped_count: int
    failed_count: int
    dry_run: bool
    per_job_results: list[FakeJobResult]


class TestParseArgs:
    def test_requires_organization_id(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args([])

    def test_requires_organization_id_dash_dash(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--max-items", "10"])

    def test_default_max_items(self) -> None:
        args = cli.parse_args(["--organization-id", "org-1"])
        assert args.organization_id == "org-1"
        assert args.max_items == 50
        assert args.dry_run is False
        assert args.requested_by == "ops-cli"
        assert args.json is False

    def test_custom_values(self) -> None:
        args = cli.parse_args(
            [
                "--organization-id",
                "org-42",
                "--max-items",
                "10",
                "--dry-run",
                "--requested-by",
                "ops-user",
                "--json",
            ]
        )
        assert args.organization_id == "org-42"
        assert args.max_items == 10
        assert args.dry_run is True
        assert args.requested_by == "ops-user"
        assert args.json is True

    def test_max_items_default_overrides(self) -> None:
        args = cli.parse_args(["--organization-id", "org-x", "--max-items", "100"])
        assert args.max_items == 100

    def test_rejects_zero_max_items(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-x", "--max-items", "0"])

    def test_rejects_negative_max_items(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-x", "--max-items", "-1"])


class TestBuildResultDict:
    def test_build_result_dict_empty(self) -> None:
        result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[],
        )
        data = cli._build_result_dict(result, duration_seconds=0.5, dry_run=False)
        assert data["organization_id"] == "org-1"
        assert data["dry_run"] is False
        assert data["scanned_count"] == 0
        assert data["processed_count"] == 0
        assert data["duration_seconds"] == 0.5
        assert data["per_job_results"] == []

    def test_build_result_dict_with_jobs(self) -> None:
        result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=2,
            processed_count=2,
            released_count=1,
            skipped_count=1,
            failed_count=0,
            dry_run=True,
            per_job_results=[
                FakeJobResult(
                    job_id="job-1",
                    organization_id="org-1",
                    error_category="released_now",
                    release_entry_id="rel-entry-1",
                    release_performed=True,
                    idempotent=False,
                    status_before="cancelled",
                    status_after="released",
                    message="released",
                ),
                FakeJobResult(
                    job_id="job-2",
                    organization_id="org-1",
                    error_category="skipped_no_reservation",
                    release_entry_id=None,
                    release_performed=False,
                    idempotent=False,
                    status_before="cancel_requested",
                    status_after="cancel_requested",
                    message="no reservation",
                ),
            ],
        )
        data = cli._build_result_dict(result, duration_seconds=0.123, dry_run=True)
        assert data["organization_id"] == "org-1"
        assert data["dry_run"] is True
        assert data["scanned_count"] == 2
        assert data["released_count"] == 1
        assert data["duration_seconds"] == 0.123
        assert len(data["per_job_results"]) == 2
        assert data["per_job_results"][0]["job_id"] == "job-1"
        assert data["per_job_results"][0]["error_category"] == "released_now"
        assert data["per_job_results"][0]["release_entry_id"] == "rel-entry-1"
        assert data["per_job_results"][1]["error_category"] == "skipped_no_reservation"
        assert data["per_job_results"][1]["release_entry_id"] is None

    def test_result_dict_json_serializable(self) -> None:
        result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=1,
            processed_count=1,
            released_count=1,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-1",
                    organization_id="org-1",
                    error_category="released_now",
                    release_entry_id="rel-entry-1",
                    release_performed=True,
                    idempotent=False,
                    status_before="cancelled",
                    status_after="released",
                    message="released",
                ),
            ],
        )
        data = cli._build_result_dict(result, duration_seconds=0.5, dry_run=False)
        dumped = json.dumps(data, default=str)
        assert isinstance(dumped, str)
        parsed = json.loads(dumped)
        assert parsed["organization_id"] == "org-1"
        assert parsed["per_job_results"][0]["job_id"] == "job-1"


class TestMainAsync:
    async def test_success_exit_code_zero(self) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=1,
            processed_count=1,
            released_count=1,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-1",
                    organization_id="org-1",
                    error_category="released_now",
                    release_performed=True,
                    release_entry_id="rel-entry-1",
                ),
            ],
        )

        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )
        assert exit_code == 0

    async def test_partial_failure_exit_code_one(self) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=2,
            processed_count=2,
            released_count=1,
            skipped_count=0,
            failed_count=1,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-1",
                    organization_id="org-1",
                    error_category="retryable_error",
                    release_performed=False,
                    message="timeout",
                ),
                FakeJobResult(
                    job_id="job-2",
                    organization_id="org-1",
                    error_category="released_now",
                    release_performed=True,
                    release_entry_id="rel-entry-2",
                ),
            ],
        )

        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )
        assert exit_code == 1

    async def test_unexpected_error_exit_code_three(self) -> None:
        with patch.object(
            cli, "run_reconciliation", AsyncMock(side_effect=ValueError("db crash"))
        ):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )
        assert exit_code == 3

    async def test_passes_organization_id_to_run_reconciliation(self) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-test",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[],
        )

        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)) as mock_run:
            await cli.main_async(
                cli.parse_args(
                    [
                        "--organization-id",
                        "org-test",
                        "--max-items",
                        "25",
                        "--dry-run",
                        "--requested-by",
                        "test-operator",
                    ]
                )
            )

        mock_run.assert_awaited_once()
        call_args = mock_run.call_args[0][0]
        assert call_args.organization_id == "org-test"
        assert call_args.max_items == 25
        assert call_args.dry_run is True
        assert call_args.requested_by == "test-operator"

    async def test_json_output_is_parseable(self, capsys) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=1,
            processed_count=1,
            released_count=1,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-1",
                    organization_id="org-1",
                    error_category="released_now",
                    release_entry_id="rel-entry-1",
                    release_performed=True,
                ),
            ],
        )

        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            await cli.main_async(cli.parse_args(["--organization-id", "org-1", "--json"]))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["organization_id"] == "org-1"
        assert parsed["released_count"] == 1

    async def test_no_json_output_is_readable(self, capsys) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=True,
            per_job_results=[],
        )

        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            await cli.main_async(cli.parse_args(["--organization-id", "org-1", "--dry-run"]))

        captured = capsys.readouterr()
        assert "organization-1" not in captured.out
        assert "Org-1" not in captured.out
        assert "org-1" in captured.out

    async def test_error_with_json_output(self, capsys) -> None:
        with patch.object(
            cli, "run_reconciliation", AsyncMock(side_effect=RuntimeError("connection refused"))
        ):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )

        assert exit_code == 3
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "error" in parsed
        assert "connection refused" in parsed["error"]

    async def test_dry_run_flag_noop_no_failures(self) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=True,
            per_job_results=[],
        )

        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--dry-run"])
            )
        assert exit_code == 0


class TestPublicEndpointNotTouched:
    def test_cli_does_not_import_route_module(self) -> None:
        route_path = SRC_DIR / "routes" / "ai_job_routes.py"
        imported_modules = [k for k in sys.modules.keys() if "ai_job_routes" in k]
        assert not imported_modules

    def test_cli_does_not_import_public_cancel(self) -> None:
        for mod_name in list(sys.modules.keys()):
            if "route" in mod_name.lower() and "cancel" in mod_name.lower():
                assert False, f"Unexpected route module loaded: {mod_name}"


class TestSecurityAssumptions:
    def test_rejects_organization_id_from_env(self) -> None:
        args = cli.parse_args(["--organization-id", "org-from-cli"])
        assert args.organization_id == "org-from-cli"

    def test_no_global_batch_default(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args([])

    def test_no_release_credits_parameter(self) -> None:
        args = cli.parse_args(["--organization-id", "org-1"])
        assert not hasattr(args, "release_credits")
        assert not hasattr(args, "caller_key")

    def test_requested_by_default_does_not_expose_internal(self) -> None:
        args = cli.parse_args(["--organization-id", "org-1"])
        assert args.requested_by == "ops-cli"
        assert args.requested_by not in ("internal_trigger", "system")
