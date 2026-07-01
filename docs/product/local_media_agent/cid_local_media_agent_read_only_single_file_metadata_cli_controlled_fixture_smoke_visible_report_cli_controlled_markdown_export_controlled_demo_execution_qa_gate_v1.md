# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Controlled Demo Execution QA Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTROLLED_DEMO.EXECUTION.QA.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTROLLED_DEMO_EXECUTION_QA_GATE_V1_CLOSED

## Purpose

Doc/test-only QA gate for the controlled demo execution.

This phase audits the already closed controlled demo execution gate. It verifies that the demo is reproducible, that the command remains bounded to the public wrapper and controlled fixture, that the temporary Markdown export is cleaned, and that no persistent report artifact is produced outside the approved temporary output root.

## Current stable base

Base HEAD: fb90fead00dff1ba196bf368deb368eec6666a7e

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-controlled-demo-execution-gate-v1-20260701

## Prior closed controlled demo execution phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTROLLED_DEMO.EXECUTION.GATE.V1

## Prior closed controlled demo execution result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTROLLED_DEMO_EXECUTION_GATE_V1_CLOSED

## Audited demo artifacts

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py

## Runtime artifacts under QA

- scripts/local_media_agent/read_only_single_file_metadata_cli.py
- scripts/local_media_agent/read_only_single_file_metadata.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Demo flags under QA

- --visible-report-markdown
- --visible-report-output

## Controlled output root

tests/tmp/local_media_agent/controlled_visible_report_exports

## Controlled demo export file

tests/tmp/local_media_agent/controlled_visible_report_exports/controlled_demo_visible_report_qa.md

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
- Prior controlled demo execution document exists.
- Prior controlled demo execution test exists.
- Prior wrapper smoke execution QA doc/test exist.
- Prior wrapper smoke execution doc/test exist.
- Prior implementation QA doc/test exist.
- Prior implementation doc/test exist.
- Public wrapper exists.
- Implementation exists.
- Renderer and in-memory integration exist.
- Prior demo document declares command shape.
- Prior demo document declares stdout validation.
- Prior demo document declares exported file SHA256 validation.
- Prior demo document declares cleanup.
- Prior demo document declares no real material.
- Prior demo test uses sys.executable.
- Prior demo test uses public wrapper.
- Prior demo test uses shell=False.
- Prior demo test uses cwd=ROOT.
- Prior demo test uses captured stdout and stderr.
- Prior demo test uses timeout.
- Prior demo test computes exported Markdown SHA256.
- Prior demo test removes the controlled output root.
- QA command uses sys.executable.
- QA command targets the public wrapper.
- QA command uses controlled fixture args.
- QA command includes expected bytes and SHA256.
- QA command includes allowed relative path.
- QA visible stdout run returns exit code 0.
- QA visible stdout run writes no stderr.
- QA visible stdout starts with the visible report title.
- QA visible stdout includes expected fixture SHA256.
- QA visible stdout includes allowed relative path.
- QA export run returns exit code 0.
- QA export stdout is CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.
- QA export writes no stderr.
- QA export creates exactly one .md inside the controlled output root.
- QA exported Markdown exactly equals captured visible stdout.
- QA exported Markdown SHA256 is 64 lowercase hexadecimal characters.
- QA exported Markdown includes the expected fixture SHA256.
- QA exported Markdown includes the allowed relative path.
- QA rejected overwrite preserves existing export content.
- QA rejected outside-root path writes nothing.
- QA rejected missing visible mode writes nothing.
- No report artifact appears at repository root.
- Temporary controlled output root is removed by the QA test.
- Controlled fixture remains byte-for-byte unchanged.
- Fixture support files remain present.

## Allowed scope

- Add this QA document.
- Add one QA unit test.
- Execute the public wrapper with sys.executable.
- Use subprocess.run only inside this QA test.
- Use shell=False only.
- Use cwd set to repository root.
- Capture stdout and stderr.
- Use timeout.
- Create temporary Markdown exports inside tests/tmp/local_media_agent/controlled_visible_report_exports.
- Compute SHA256 of temporary exported Markdown.
- Remove temporary controlled exports after test.
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
- No unsafe shell execution.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate.py
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

- New controlled demo execution QA test passes.
- Related controlled demo execution, wrapper smoke execution QA, wrapper smoke execution, implementation QA, implementation, wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this QA document and QA unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export controlled demo execution QA gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-controlled-demo-execution-qa-gate-v1-20260701
