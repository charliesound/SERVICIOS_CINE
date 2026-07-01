# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI In-memory Report Implementation Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.IMPLEMENTATION.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_IMPLEMENTATION_GATE_V1_CLOSED

## Purpose

Controlled implementation gate for the explicit CLI visible report Markdown mode.

This phase implements only the opt-in --visible-report-markdown CLI mode. It keeps default CLI status output unchanged, keeps --result-json behavior unchanged, prints Markdown to stdout only for the explicit visible report flag, and does not write report files or add export behavior.

## Current stable base

Base HEAD: 1c77336b8ab5560bb3429e0619aeeb2448fab068

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-readiness-gate-v1-20260701

## Modified implementation artifact

scripts/local_media_agent/read_only_single_file_metadata.py

## Unmodified wrapper artifact

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Existing in-memory integration artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py

## Existing renderer artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Implemented CLI mode

--visible-report-markdown

## Prior source chain

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py
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

## Implementation contract

The implementation must:

- Add --visible-report-markdown to the parser.
- Keep the visible report mode explicit and opt-in.
- Keep default CLI behavior unchanged.
- Keep existing --result-json behavior unchanged.
- Build structured controlled fixture smoke result data in memory.
- Pass structured data to render_controlled_fixture_smoke_result_in_memory through the existing in-memory integration.
- Print Markdown to stdout only when --visible-report-markdown is used.
- Preserve deterministic exit code behavior.
- Return 0 for accepted controlled fixture metadata.
- Return 2 for rejected controlled fixture metadata.
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

## Allowed scope

- Add this implementation document.
- Modify scripts/local_media_agent/read_only_single_file_metadata.py only for explicit visible report Markdown mode.
- Add one implementation unit test.
- Verify controlled fixture integrity.
- Keep wrapper unchanged.
- Keep output in stdout only.

## Forbidden scope

- No wrapper behavior changes.
- No report file generation.
- No export behavior.
- No persistent output path.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New CLI in-memory report implementation test passes.
- Related CLI in-memory report readiness, integration QA, integration implementation, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this implementation document, implementation unit test, and read_only_single_file_metadata.py are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

feat: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke visible report CLI in-memory report implementation gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-implementation-gate-v1-20260701
