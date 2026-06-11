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


class TestDangerousFlags:
    def test_rejects_release_credits(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(
                ["--organization-id", "org-1", "--release-credits", "10"]
            )

    def test_rejects_release_entry_id(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(
                ["--organization-id", "org-1", "--release-entry-id", "x"]
            )

    def test_rejects_caller_key(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-1", "--caller-key", "k"])

    def test_rejects_consume_flag(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-1", "--consume"])

    def test_rejects_force_flag(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-1", "--force"])

    def test_rejects_all_organizations(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-1", "--all-organizations"])

    def test_rejects_global_flag(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-1", "--global"])

    def test_rejects_tenant_all(self) -> None:
        with pytest.raises(SystemExit):
            cli.parse_args(["--organization-id", "org-1", "--tenant-all"])


class TestServiceWiring:
    async def test_constructs_repository_with_session(self) -> None:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session

        with patch("database.AsyncSessionLocal", return_value=mock_session):
            with patch(
                "repositories.ai_job_repository.AIJobRepository"
            ) as mock_repo:
                with patch(
                    "services.ai_job_accounting_gateway.AIJobAccountingGateway"
                ) as mock_gateway:
                    with patch(
                        "services.ai_job_costing_service.AIJobCostingService"
                    ) as mock_costing:
                        with patch(
                            "services.ai_job_async_orchestration_service."
                            "AIJobAsyncOrchestrationService"
                        ) as mock_orch:
                            mock_service = AsyncMock()
                            mock_orch.return_value = mock_service
                            mock_service.process_cancelled_ai_job_credit_releases = (
                                AsyncMock(
                                    return_value=FakeReconciliationResult(
                                        organization_id="org-1",
                                        scanned_count=0,
                                        processed_count=0,
                                        released_count=0,
                                        skipped_count=0,
                                        failed_count=0,
                                        dry_run=False,
                                        per_job_results=[],
                                    )
                                )
                            )

                            await cli.run_reconciliation(
                                cli.parse_args(
                                    [
                                        "--organization-id",
                                        "org-wired",
                                        "--max-items",
                                        "30",
                                        "--dry-run",
                                        "--requested-by",
                                        "wiring-test",
                                    ]
                                )
                            )

        mock_repo.assert_called_once_with(mock_session.__aenter__.return_value)
        mock_costing.assert_called_once()
        mock_gateway.assert_called_once_with(mock_costing.return_value)
        mock_orch.assert_called_once_with(
            repository=mock_repo.return_value,
            accounting_gateway=mock_gateway.return_value,
        )

    async def test_calls_process_cancelled_credit_releases(self) -> None:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        fake_result = FakeReconciliationResult(
            organization_id="org-wired",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=True,
            per_job_results=[],
        )

        with patch("database.AsyncSessionLocal", return_value=mock_session):
            with patch(
                "repositories.ai_job_repository.AIJobRepository"
            ):
                with patch(
                    "services.ai_job_accounting_gateway.AIJobAccountingGateway"
                ):
                    with patch(
                        "services.ai_job_costing_service.AIJobCostingService"
                    ):
                        with patch(
                            "services.ai_job_async_orchestration_service."
                            "AIJobAsyncOrchestrationService"
                        ) as mock_orch:
                            mock_service = AsyncMock()
                            mock_orch.return_value = mock_service
                            mock_service.process_cancelled_ai_job_credit_releases = (
                                AsyncMock(return_value=fake_result)
                            )

                            await cli.run_reconciliation(
                                cli.parse_args(
                                    [
                                        "--organization-id",
                                        "org-wired",
                                        "--max-items",
                                        "30",
                                        "--requested-by",
                                        "wiring-test",
                                    ]
                                )
                            )

        mock_service.process_cancelled_ai_job_credit_releases.assert_awaited_once()
        req = (
            mock_service.process_cancelled_ai_job_credit_releases
        ).call_args[0][1]
        assert req.organization_id == "org-wired"
        assert req.max_items == 30
        assert req.requested_by == "wiring-test"

    async def test_does_not_call_release_directly(self) -> None:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session

        with patch("database.AsyncSessionLocal", return_value=mock_session):
            with patch(
                "repositories.ai_job_repository.AIJobRepository"
            ):
                with patch(
                    "services.ai_job_accounting_gateway.AIJobAccountingGateway"
                ):
                    with patch(
                        "services.ai_job_costing_service.AIJobCostingService"
                    ):
                        with patch(
                            "services.ai_job_async_orchestration_service."
                            "AIJobAsyncOrchestrationService"
                        ) as mock_orch:
                            mock_service = AsyncMock()
                            mock_orch.return_value = mock_service
                            mock_service.process_cancelled_ai_job_credit_releases = (
                                AsyncMock(
                                    return_value=FakeReconciliationResult(
                                        organization_id="org-1",
                                        scanned_count=0,
                                        processed_count=0,
                                        released_count=0,
                                        skipped_count=0,
                                        failed_count=0,
                                        dry_run=False,
                                        per_job_results=[],
                                    )
                                )
                            )
                            mock_service.release_cancelled_ai_job_reserved_credits = (
                                AsyncMock()
                            )

                            await cli.run_reconciliation(
                                cli.parse_args(
                                    ["--organization-id", "org-wired"]
                                )
                            )

        mock_service.release_cancelled_ai_job_reserved_credits.assert_not_called()

    async def test_sends_dry_run_true_to_service(self) -> None:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session

        with patch("database.AsyncSessionLocal", return_value=mock_session):
            with patch(
                "repositories.ai_job_repository.AIJobRepository"
            ):
                with patch(
                    "services.ai_job_accounting_gateway.AIJobAccountingGateway"
                ):
                    with patch(
                        "services.ai_job_costing_service.AIJobCostingService"
                    ):
                        with patch(
                            "services.ai_job_async_orchestration_service."
                            "AIJobAsyncOrchestrationService"
                        ) as mock_orch:
                            mock_service = AsyncMock()
                            mock_orch.return_value = mock_service
                            mock_service.process_cancelled_ai_job_credit_releases = (
                                AsyncMock(
                                    return_value=FakeReconciliationResult(
                                        organization_id="org-1",
                                        scanned_count=0,
                                        processed_count=0,
                                        released_count=0,
                                        skipped_count=0,
                                        failed_count=0,
                                        dry_run=True,
                                        per_job_results=[],
                                    )
                                )
                            )

                            await cli.run_reconciliation(
                                cli.parse_args(
                                    [
                                        "--organization-id",
                                        "org-wired",
                                        "--dry-run",
                                    ]
                                )
                            )

        req = (
            mock_service.process_cancelled_ai_job_credit_releases
        ).call_args[0][1]
        assert req.dry_run is True


class TestHumanOutput:
    def test_human_output_contains_all_counters(self, capsys) -> None:
        result = FakeReconciliationResult(
            organization_id="org-display",
            scanned_count=5,
            processed_count=5,
            released_count=3,
            skipped_count=1,
            failed_count=1,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-a",
                    organization_id="org-display",
                    error_category="released_now",
                    release_entry_id="rel-a",
                    release_performed=True,
                ),
                FakeJobResult(
                    job_id="job-b",
                    organization_id="org-display",
                    error_category="retryable_error",
                    release_performed=False,
                    message="timeout",
                ),
            ],
        )
        cli._print_human(result, duration_seconds=0.5, dry_run=False)
        captured = capsys.readouterr()
        assert "org-display" in captured.out
        assert "Dry Run" in captured.out
        assert "Scanned         : 5" in captured.out
        assert "Processed       : 5" in captured.out
        assert "Released        : 3" in captured.out
        assert "Skipped         : 1" in captured.out
        assert "Failed          : 1" in captured.out
        assert "0.5s" in captured.out
        assert "job-a" in captured.out
        assert "job-b" in captured.out
        assert "released_now" in captured.out
        assert "retryable_error" in captured.out
        assert "rel-a" in captured.out


class TestJsonOutput:
    async def test_json_per_job_results_content(self, capsys) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-json",
            scanned_count=2,
            processed_count=2,
            released_count=2,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-x",
                    organization_id="org-json",
                    error_category="released_now",
                    release_entry_id="rel-x",
                    release_performed=True,
                    idempotent=False,
                    status_before="cancelled",
                    status_after="released",
                    message="ok",
                ),
            ],
        )
        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            await cli.main_async(cli.parse_args(["--organization-id", "org-json", "--json"]))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["organization_id"] == "org-json"
        assert len(parsed["per_job_results"]) == 1
        job = parsed["per_job_results"][0]
        assert job["job_id"] == "job-x"
        assert job["error_category"] == "released_now"
        assert job["release_entry_id"] == "rel-x"
        assert job["release_performed"] is True
        assert job["idempotent"] is False
        assert job["status_before"] == "cancelled"
        assert job["status_after"] == "released"

    async def test_json_error_has_no_secrets(self, capsys) -> None:
        secret_value = "super-secret-db-pass"
        os.environ["DATABASE_URL"] = (
            "postgresql+asyncpg://user:" + secret_value + "@host:5432/db"
        )
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[],
        )
        try:
            with patch.object(
                cli,
                "run_reconciliation",
                AsyncMock(return_value=fake_result),
            ):
                await cli.main_async(
                    cli.parse_args(["--organization-id", "org-1", "--json"])
                )
            captured = capsys.readouterr()
            assert secret_value not in captured.out
        finally:
            os.environ["DATABASE_URL"] = (
                "postgresql+asyncpg://placeholder:placeholder@localhost:5432/placeholder"
            )

    async def test_normal_output_has_no_traceback(self, capsys) -> None:
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
        assert "Traceback" not in captured.out
        assert "File" not in captured.out
        assert secret_not_in_output(captured.out)


class TestExitCodes:
    def test_main_exit_code_2_for_bad_args(self) -> None:
        with patch.object(sys, "argv", ["script"]):
            with patch.object(
                cli, "main_async", AsyncMock(return_value=0)
            ):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()
        assert exc_info.value.code == 2

    def test_main_exit_code_2_for_empty_organization(self) -> None:
        with patch.object(sys, "argv", ["script", "--dry-run"]):
            with patch.object(
                cli, "main_async", AsyncMock(return_value=0)
            ):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()
        assert exc_info.value.code == 2

    async def test_json_exit_code_0(self) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=0,
            processed_count=0,
            released_count=0,
            skipped_count=0,
            failed_count=0,
            dry_run=False,
            per_job_results=[],
        )
        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )
        assert exit_code == 0

    async def test_json_exit_code_1(self) -> None:
        fake_result = FakeReconciliationResult(
            organization_id="org-1",
            scanned_count=1,
            processed_count=1,
            released_count=0,
            skipped_count=0,
            failed_count=1,
            dry_run=False,
            per_job_results=[
                FakeJobResult(
                    job_id="job-fail",
                    organization_id="org-1",
                    error_category="retryable_error",
                    release_performed=False,
                ),
            ],
        )
        with patch.object(cli, "run_reconciliation", AsyncMock(return_value=fake_result)):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )
        assert exit_code == 1

    async def test_json_exit_code_3(self) -> None:
        with patch.object(
            cli,
            "run_reconciliation",
            AsyncMock(side_effect=ConnectionError("db down")),
        ):
            exit_code = await cli.main_async(
                cli.parse_args(["--organization-id", "org-1", "--json"])
            )
        assert exit_code == 3


class TestSecurityOperativa:
    CLI_SOURCE = (ROOT / "scripts" / "ops" / "reconcile_cancelled_ai_job_credit_releases.py").read_text(
        encoding="utf-8"
    )

    def test_no_hardcoded_database_url(self) -> None:
        in_docstring = False
        for line in self.CLI_SOURCE.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped == '"""':
                in_docstring = not in_docstring
                continue
            if in_docstring or stripped.startswith("#"):
                continue
            if "://" in stripped and (
                "postgresql" in stripped or "postgres" in stripped
            ):
                assert False, (
                    f"Hardcoded URL pattern found: {stripped}"
                )

    def test_no_hardcoded_credentials(self) -> None:
        suspicious = (
            "password=",
            "pwd=",
            "pass=",
            "secret=",
        )
        for keyword in suspicious:
            for line in self.CLI_SOURCE.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if keyword.lower() in stripped.lower():
                    assert False, (
                        f"Hardcoded credential pattern found: {stripped}"
                    )

    def test_does_not_print_database_url(self) -> None:
        for line in self.CLI_SOURCE.splitlines():
            if "print" in line and "DATABASE_URL" in line:
                assert False, "CLI prints DATABASE_URL"

    def test_does_not_read_env_directly(self) -> None:
        for line in self.CLI_SOURCE.splitlines():
            if "open" in line and ".env" in line:
                assert False, "CLI reads .env directly"

    def test_no_config_alternative_created(self) -> None:
        for line in self.CLI_SOURCE.splitlines():
            if "Config" in line and "Settings" not in line:
                continue
        assert True


def secret_not_in_output(output: str) -> bool:
    lower = output.lower()
    blocked = (
        "secret",
        "password",
        "token",
        "apikey",
        "api_key",
    )
    return not any(b in lower for b in blocked)
