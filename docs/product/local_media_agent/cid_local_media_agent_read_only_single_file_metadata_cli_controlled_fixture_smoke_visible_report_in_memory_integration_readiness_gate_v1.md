# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report In-memory Integration Readiness Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.IN_MEMORY.INTEGRATION.READINESS.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_IN_MEMORY_INTEGRATION_READINESS_GATE_V1_CLOSED

## Purpose

Doc/test-only readiness gate for a future in-memory integration between controlled fixture smoke evidence and the visible report renderer.

This phase prepares the integration contract only. It does not implement the integration, does not change CLI behavior, does not change renderer behavior, does not generate report files, does not add export behavior, and does not execute against real or customer material.

## Current stable base

Base HEAD: 71277ef3c3b278defceaf3e173d6e3c1abb3f6a8

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-renderer-implementation-qa-gate-v1-20260701

## Existing renderer artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Future integration artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py

The future integration artifact is not implemented in this phase.

## Prior source chain

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py

## Controlled fixture identity

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Future integration contract

The future implementation must:

- Accept structured controlled fixture smoke result data in memory.
- Pass that structured data to render_controlled_fixture_smoke_visible_report.
- Return Markdown text in memory.
- Preserve the smoke result data without mutation.
- Preserve controlled fixture identity values.
- Preserve byte size and SHA256 digest values.
- Preserve smoke status, exit code, stdout validation, stderr validation, fixture immutability, and output creation status.
- Preserve human review and next allowed phase placeholders.
- Avoid any filesystem writes.
- Avoid any report export behavior.
- Avoid CLI behavior changes.
- Avoid scanner integration.
- Avoid media probing.
- Avoid subprocess and shell execution.

## Required readiness checks

The readiness test must verify:

- This document exists.
- This document declares the phase and result identifiers.
- This document references the current stable base.
- This document references the renderer implementation QA gate.
- This document references the renderer implementation gate.
- This document references the renderer readiness gate.
- This document references the visible report contract gate.
- The renderer artifact exists and exposes render_controlled_fixture_smoke_visible_report.
- The renderer still has safe minimal imports.
- The renderer remains free of file write, process execution, scan, and media probe calls.
- The controlled fixture remains byte-for-byte unchanged.
- pyproject does not register the renderer or future integration as console scripts.

## Allowed scope

- Add this readiness document.
- Add one readiness unit test.
- Audit the existing renderer enough to confirm it is ready for in-memory integration.
- Verify controlled fixture integrity.
- Keep this phase doc/test-only.

## Forbidden scope

- No integration implementation.
- No renderer behavior changes.
- No CLI behavior changes.
- No CLI execution.
- No report file generation.
- No export behavior.
- No new smoke scenario.
- No subprocess.
- No shell execution.
- No fixture modification.
- No scanner integration.
- No batch processing.
- No recursive product traversal.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New in-memory integration readiness test passes.
- Related renderer QA, renderer implementation, visible report contract, smoke QA, and CLI contract tests pass.
- Mandatory guards pass.
- Only this readiness document and readiness unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke visible report in-memory integration readiness gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-in-memory-integration-readiness-gate-v1-20260701
