# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Implementation QA Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.IMPLEMENTATION.QA.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_IMPLEMENTATION_QA_GATE_V1_CLOSED

## Purpose

Doc/test-only QA gate for the controlled Markdown export implementation.

This phase audits the already implemented --visible-report-output behavior from outside the implementation gate. It verifies that the parser exposes the flag, that export remains confined to the controlled output root, that unsafe paths are rejected, and that default, JSON, and stdout Markdown behavior remain stable.

## Current stable base

Base HEAD: 20fc9d47c7194b3d39549eb0c4e871ad0f362270

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-implementation-gate-v1-20260701

## Prior closed implementation phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.IMPLEMENTATION.GATE.V1

## Prior closed implementation result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_IMPLEMENTATION_GATE_V1_CLOSED

## Audited implementation artifacts

- scripts/local_media_agent/read_only_single_file_metadata.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py

## Runtime artifacts that must remain unchanged by this QA phase

- scripts/local_media_agent/read_only_single_file_metadata_cli.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Implemented CLI flag under QA

--visible-report-output

## Required companion mode

--visible-report-markdown

## Existing JSON flag

--result-json

## Controlled output root

tests/tmp/local_media_agent/controlled_visible_report_exports

## Controlled fixture identity

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

Existing baseline support files inside fixture:

- README.md
- manifest.controlled.json

These are baseline fixture support files, not generated report artifacts.

## QA audit requirements

The QA test must verify:

- This QA document exists.
- Prior implementation document exists.
- Prior implementation test exists.
- Implementation file exists.
- Wrapper file exists.
- Renderer and in-memory integration files exist.
- The parser exposes --visible-report-output.
- The parser exposes --visible-report-markdown.
- The parser exposes --result-json.
- The wrapper remains a delegating layer.
- The wrapper does not implement --visible-report-output.
- The implementation source contains the controlled output root.
- The implementation source contains the export success status.
- The implementation source contains the export rejected status.
- The implementation source rejects output use without --visible-report-markdown.
- The implementation source rejects Windows-style path strings.
- The implementation source rejects symlink output files.
- The implementation source rejects symlink parent directories.
- The implementation source rejects tests/fixtures paths.
- The implementation source rejects controlled fixture root paths.
- The implementation source rejects overwrite by default.
- The implementation source rejects non-.md suffixes.
- The implementation source does not import subprocess.
- The implementation source does not use shell execution.
- The implementation source does not register pyproject console scripts.
- Default status behavior remains exact.
- --result-json behavior remains exact enough for schema, status, bytes, and SHA256.
- --visible-report-markdown stdout behavior remains exact enough for title, fixture path, bytes, and SHA256.
- Valid controlled export writes exactly one .md file.
- Exported Markdown exactly matches the in-memory Markdown stdout.
- Export without --visible-report-markdown is rejected and writes nothing.
- Existing file overwrite is rejected and preserves existing content.
- Missing parent path is rejected.
- Non-.md suffix is rejected.
- Output outside controlled root is rejected.
- Windows-style path string is rejected.
- Fixture source tree output is rejected.
- tests/fixtures output is rejected.
- Rejected metadata writes nothing.
- Controlled fixture remains byte-for-byte unchanged.
- Fixture support files remain present.
- No root report artifacts are created.

## Allowed scope

- Add this QA document.
- Add one QA unit test.
- Use tests/tmp/local_media_agent/controlled_visible_report_exports as temporary controlled export root during the QA test.
- Create and remove temporary test exports inside the controlled export root.
- Audit implementation behavior in-process through run_cli.
- Keep this phase doc/test-only.

## Forbidden scope

- No implementation changes.
- No parser changes.
- No CLI behavior changes.
- No wrapper behavior changes.
- No renderer behavior changes.
- No in-memory integration behavior changes.
- No report export outside controlled test root.
- No persistent output artifacts.
- No fixture modification.
- No scanner integration.
- No batch processing.
- No recursive product traversal.
- No FFmpeg.
- No ffprobe.
- No subprocess.
- No shell execution.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New controlled Markdown export implementation QA test passes.
- Related implementation, wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this QA document and QA unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export implementation QA gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-implementation-qa-gate-v1-20260701
