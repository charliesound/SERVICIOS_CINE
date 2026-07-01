# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Controlled Demo Execution Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTROLLED_DEMO.EXECUTION.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTROLLED_DEMO_EXECUTION_GATE_V1_CLOSED

## Purpose

Doc/test-only controlled demo execution gate for the public wrapper flow.

This phase simulates an internal demo run using the public wrapper, the controlled non-customer fixture, visible Markdown stdout, and controlled Markdown export. It validates command shape, stdout, exported file content, exported file SHA256, cleanup, and security boundaries without using real or customer material.

## Current stable base

Base HEAD: eb45a48989ccda81be032edbfc6bb30524e6a57c

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-wrapper-smoke-execution-qa-gate-v1-20260701

## Prior closed wrapper smoke execution QA phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.WRAPPER.SMOKE.EXECUTION.QA.GATE.V1

## Prior closed wrapper smoke execution QA result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_WRAPPER_SMOKE_EXECUTION_QA_GATE_V1_CLOSED

## Demo wrapper

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Demo implementation

scripts/local_media_agent/read_only_single_file_metadata.py

## Demo controlled fixture

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Demo CLI modes

The controlled demo must exercise:

- --visible-report-markdown
- --visible-report-markdown with --visible-report-output

## Demo controlled output root

tests/tmp/local_media_agent/controlled_visible_report_exports

## Demo export file

tests/tmp/local_media_agent/controlled_visible_report_exports/controlled_demo_visible_report.md

## Controlled demo evidence to validate in test

The test must validate:

- This demo document exists.
- Prior wrapper smoke execution QA doc/test exist.
- Prior wrapper smoke execution doc/test exist.
- Implementation QA doc/test exist.
- Implementation gate doc/test exist.
- Public wrapper exists.
- Implementation exists.
- Renderer and in-memory integration exist.
- The demo command uses sys.executable.
- The demo command targets scripts/local_media_agent/read_only_single_file_metadata_cli.py.
- The demo command uses the controlled fixture root.
- The demo command uses the controlled target path.
- The demo command includes expected bytes and SHA256.
- The demo command includes the allowed relative path.
- The visible stdout demo returns exit code 0.
- The visible stdout demo writes no stderr.
- The visible stdout demo starts with the visible report title.
- The visible stdout demo includes expected SHA256.
- The visible stdout demo includes allowed relative path.
- The export demo returns exit code 0.
- The export demo stdout is CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.
- The export demo writes no stderr.
- The export demo creates exactly one .md file inside the controlled output root.
- The exported .md content exactly equals the captured visible Markdown stdout.
- The exported .md SHA256 is computed and deterministic for the run.
- The exported .md SHA256 is 64 lowercase hexadecimal characters.
- The exported .md includes the expected fixture SHA256.
- The exported .md includes the allowed relative path.
- No report artifact appears at repository root.
- Temporary export root is removed by the test.
- Controlled fixture remains byte-for-byte unchanged.
- Fixture support files remain present.

## Allowed scope

- Add this controlled demo execution document.
- Add one controlled demo execution unit test.
- Execute the public wrapper with sys.executable.
- Use subprocess.run only inside this controlled demo test.
- Use shell=False only.
- Use cwd set to repository root.
- Capture stdout and stderr.
- Use timeout.
- Create one temporary Markdown export inside tests/tmp/local_media_agent/controlled_visible_report_exports.
- Compute SHA256 of the temporary exported Markdown.
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

- New controlled demo execution test passes.
- Related wrapper smoke execution QA, wrapper smoke execution, implementation QA, implementation, wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this demo execution document and demo execution unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export controlled demo execution gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-controlled-demo-execution-gate-v1-20260701
