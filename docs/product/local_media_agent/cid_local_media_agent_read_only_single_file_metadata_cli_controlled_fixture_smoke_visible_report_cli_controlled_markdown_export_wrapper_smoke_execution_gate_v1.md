# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Wrapper Smoke Execution Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED

## Purpose

Doc/test-only smoke execution gate for the public wrapper using the implemented controlled Markdown export.

This phase executes the public wrapper script with the controlled fixture and verifies that --visible-report-markdown combined with --visible-report-output creates exactly one controlled Markdown file inside the approved temporary output root.

## Current stable base

Base HEAD: 17e6b81d5209e1c2ad5fce4dde45a4f355483474

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-implementation-qa-gate-v1-20260701

## Prior closed implementation QA phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.IMPLEMENTATION.QA.GATE.V1

## Prior closed implementation QA result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_IMPLEMENTATION_QA_GATE_V1_CLOSED

## Wrapper under smoke

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Implementation under smoke

scripts/local_media_agent/read_only_single_file_metadata.py

## Implemented export flag under smoke

--visible-report-output

## Required companion mode

--visible-report-markdown

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

## Smoke execution requirements

The smoke test must verify:

- This smoke document exists.
- The public wrapper exists.
- The implementation exists.
- Prior implementation QA doc/test exist.
- The wrapper remains a delegating layer.
- The wrapper does not parse arguments itself.
- The wrapper does not contain --visible-report-output.
- The wrapper does not contain --visible-report-markdown.
- The implementation parser exposes --visible-report-output.
- The smoke execution uses the public wrapper script through the active Python interpreter.
- The smoke execution uses shell=False.
- The smoke execution uses cwd set to the repository root.
- The smoke execution captures stdout and stderr.
- The smoke execution uses a timeout.
- The smoke execution first captures the Markdown stdout produced by --visible-report-markdown.
- The smoke execution then exports with --visible-report-markdown and --visible-report-output.
- Valid export returns exit code 0.
- Valid export stdout is CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.
- Valid export stderr is empty.
- Exactly one .md file is created inside tests/tmp/local_media_agent/controlled_visible_report_exports.
- The exported Markdown exactly equals the captured stdout Markdown.
- The exported Markdown includes the expected SHA256.
- The exported Markdown includes the allowed relative path.
- Export without --visible-report-markdown is rejected.
- Export outside the controlled root is rejected.
- Export to a non-.md suffix is rejected.
- Export overwrite is rejected.
- Rejected export attempts create no extra files.
- The controlled fixture remains byte-for-byte unchanged.
- Fixture support files remain present.
- No root report artifacts are created.
- Temporary controlled exports are removed by the test.

## Allowed scope

- Add this smoke execution document.
- Add one smoke execution unit test.
- Execute the wrapper with sys.executable.
- Use subprocess.run only inside this smoke test.
- Use shell=False only.
- Use cwd set to the repository root.
- Use tests/tmp/local_media_agent/controlled_visible_report_exports as temporary controlled export root.
- Create and remove temporary controlled .md exports inside that root.
- Keep this phase doc/test-only.

## Forbidden scope

- No implementation changes.
- No parser changes.
- No CLI behavior changes.
- No wrapper changes.
- No renderer changes.
- No in-memory integration changes.
- No export outside controlled test root.
- No persistent output artifacts.
- No fixture modification.
- No scanner integration.
- No batch processing.
- No recursive product traversal.
- No FFmpeg.
- No ffprobe.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New controlled Markdown export wrapper smoke execution test passes.
- Related implementation QA, implementation, wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this smoke document and smoke unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export wrapper smoke execution gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-wrapper-smoke-execution-gate-v1-20260701
