# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report Contract V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CONTRACT.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CONTRACT_V1_CLOSED

## Purpose

Doc/test-only contract for a future visible report generated from the controlled fixture smoke execution evidence.

This phase defines the visible report shape and audit boundaries. It does not change CLI behavior, does not generate a report file, does not add export behavior, and does not execute against real or customer material.

## Current stable base

Base HEAD: 18663935de2bf0c8975b40cf0d220d6c16fe7e3a

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-execution-qa-gate-v1-20260701

## Audited source evidence

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py

## Controlled fixture identity

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Visible report contract

The future visible report must be human-readable and must include these sections:

- Report title.
- Phase identifier.
- Result identifier.
- Smoke status.
- Controlled fixture identity.
- Fixture root.
- Allowed relative path.
- File name.
- Byte size.
- SHA256 digest.
- CLI execution mode.
- Exit code.
- JSON stdout validation status.
- Stderr validation status.
- Fixture immutability status.
- Output file creation status.
- Forbidden boundary checklist.
- Human review decision placeholder.
- Next allowed phase placeholder.

## Required report values for this controlled fixture

- Smoke status: PASS.
- Fixture id: controlled_plain_text_marker_v1.
- Allowed relative path: media/controlled_plain_text_marker.txt.
- File name: controlled_plain_text_marker.txt.
- Byte size: 239.
- SHA256 digest: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a.
- CLI execution mode: isolated main argv smoke.
- Exit code: 0.
- JSON stdout validation status: PASS.
- Stderr validation status: PASS_EMPTY.
- Fixture immutability status: PASS_UNCHANGED.
- Output file creation status: PASS_NONE_CREATED.
- Human review decision placeholder: PENDING_HUMAN_REVIEW.

## Forbidden report content

The future visible report must not include:

- Absolute user home paths.
- Machine-specific private paths outside the repository root.
- Secrets.
- Environment variables.
- Customer names.
- Real production titles.
- Real media metadata.
- Real material references.
- Customer material references.
- Full stdout dumps unless explicitly scoped by a later phase.
- Full stderr dumps unless explicitly scoped by a later phase.

## Allowed scope

- Add this visible report contract document.
- Add one visible report contract unit test.
- Audit existing smoke execution and QA evidence.
- Define the future report shape.
- Keep the phase doc/test-only.

## Forbidden scope

- No CLI behavior changes.
- No visible report renderer implementation.
- No report file generation.
- No export behavior.
- No new runtime execution.
- No new smoke scenario.
- No subprocess.
- No shell execution.
- No fixture modification.
- No scanner integration.
- No FFmpeg.
- No ffprobe.
- No pyproject modification.
- No console script registration.
- No SaaS integration.
- No database access.
- No backend changes.
- No frontend changes.
- No installer work.
- No Docker work.
- No Alembic work.
- No Stripe work.
- No AI Jobs work.
- No credits or ledger work.
- No real material.
- No customer material.

## Required validation commands

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New visible report contract test passes.
- Related smoke, QA, readiness, implementation, and CLI contract tests pass.
- Mandatory guards pass.
- Only this visible report contract document and contract unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke visible report contract

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-contract-v1-20260701
