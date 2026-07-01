# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI In-memory Report Readiness Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.READINESS.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_READINESS_GATE_V1_CLOSED

## Purpose

Doc/test-only readiness gate for a future explicit CLI-controlled visible report mode that can render Markdown in memory and print it to standard output.

This phase prepares the future CLI report contract only. It does not implement a CLI flag, does not change CLI behavior, does not change renderer behavior, does not change in-memory integration behavior, does not generate report files, does not add export behavior, and does not execute against real or customer material.

## Current stable base

Base HEAD: 0c6963e348072d8901513e7a89289cc6e25c831b

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-in-memory-integration-implementation-qa-gate-v1-20260701

## Existing CLI artifact

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Existing in-memory integration artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py

## Existing renderer artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Future CLI mode

Future explicit flag name reserved by this readiness gate:

--visible-report-markdown

The future flag is not implemented in this phase.

## Prior source chain

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py

## Controlled fixture identity

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Future CLI report contract

The future implementation must:

- Keep the visible report mode explicit and opt-in.
- Use the reserved --visible-report-markdown flag.
- Keep the current default CLI behavior unchanged.
- Keep existing --result-json behavior unchanged.
- Build structured controlled fixture smoke result data in memory.
- Pass structured data to render_controlled_fixture_smoke_result_in_memory.
- Print Markdown to stdout only when the explicit visible report flag is used.
- Avoid writing report files.
- Avoid adding export behavior.
- Avoid adding persistent report paths.
- Avoid scanning folders.
- Avoid media probing.
- Avoid subprocess and shell execution.
- Avoid real or customer material.
- Preserve controlled fixture identity values.
- Preserve byte size and SHA256 digest values.
- Preserve smoke status, exit code, stdout validation, stderr validation, fixture immutability, and output creation status.
- Preserve human review and next allowed phase placeholders.
- Preserve non-zero exit behavior for validation failures.

## Required readiness checks

The readiness test must verify:

- This document exists.
- This document declares the phase and result identifiers.
- This document references the current stable base.
- This document references the existing CLI artifact.
- This document references the in-memory integration implementation QA gate.
- This document references the in-memory integration implementation gate.
- This document references the in-memory integration readiness gate.
- This document references the renderer implementation QA gate.
- This document references the visible report contract gate.
- The existing CLI artifact exists and is Python parseable.
- The existing CLI artifact exposes main.
- The existing in-memory integration artifact exists and exposes render_controlled_fixture_smoke_result_in_memory.
- The existing renderer artifact exists and exposes render_controlled_fixture_smoke_visible_report.
- The existing integration can still return Markdown in memory from structured controlled fixture smoke data.
- The controlled fixture remains byte-for-byte unchanged.
- pyproject does not register the future report mode as a console script.

## Allowed scope

- Add this readiness document.
- Add one readiness unit test.
- Audit the existing CLI, integration, and renderer enough to confirm readiness.
- Verify controlled fixture integrity.
- Keep this phase doc/test-only.

## Forbidden scope

- No CLI behavior changes.
- No CLI flag implementation.
- No CLI execution.
- No renderer behavior changes.
- No in-memory integration behavior changes.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New CLI in-memory report readiness test passes.
- Related integration QA, integration implementation, renderer QA, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this readiness document and readiness unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke visible report CLI in-memory report readiness gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-readiness-gate-v1-20260701
