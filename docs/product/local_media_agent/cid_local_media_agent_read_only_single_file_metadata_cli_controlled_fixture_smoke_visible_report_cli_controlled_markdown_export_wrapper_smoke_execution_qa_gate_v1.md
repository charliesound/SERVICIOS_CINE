# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Wrapper Smoke Execution QA Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.WRAPPER.SMOKE.EXECUTION.QA.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_WRAPPER_SMOKE_EXECUTION_QA_GATE_V1_CLOSED

## Purpose

Doc/test-only QA gate for the public wrapper smoke execution with controlled Markdown export.

This phase audits the already closed wrapper smoke execution gate. It verifies that the smoke test is bounded, that subprocess execution is limited to the controlled test, that the public wrapper remains a thin delegating layer, and that controlled Markdown export still creates no persistent artifacts outside the approved temporary output root.

## Current stable base

Base HEAD: 0c4168e6ba0e720d3d05ee8037df4bea6b62b953

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-wrapper-smoke-execution-gate-v1-20260701

## Prior closed wrapper smoke execution phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1

## Prior closed wrapper smoke execution result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED

## Audited smoke artifacts

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py

## Runtime artifacts under QA

- scripts/local_media_agent/read_only_single_file_metadata_cli.py
- scripts/local_media_agent/read_only_single_file_metadata.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Implemented export flag under QA

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
- The prior wrapper smoke document exists.
- The prior wrapper smoke test exists.
- The implementation QA doc/test exist.
- The implementation gate doc/test exist.
- The wrapper exists.
- The implementation exists.
- Renderer and in-memory integration exist.
- The prior smoke document declares subprocess.run is allowed only inside the smoke test.
- The prior smoke document declares shell=False.
- The prior smoke document declares controlled output root.
- The prior smoke document declares no persistent output artifacts.
- The prior smoke test uses subprocess.run.
- The prior smoke test uses sys.executable.
- The prior smoke test uses shell=False.
- The prior smoke test uses cwd=ROOT.
- The prior smoke test uses capture_output=True.
- The prior smoke test uses text=True.
- The prior smoke test uses a timeout.
- The prior smoke test does not contain unsafe shell execution.
- The public wrapper remains a delegating layer.
- The public wrapper does not implement --visible-report-output.
- The public wrapper does not implement --visible-report-markdown.
- The implementation parser still exposes --visible-report-output.
- The implementation parser still exposes --visible-report-markdown.
- The implementation parser still exposes --result-json.
- A QA-level wrapper export still creates exactly one .md file inside the controlled root.
- Exported Markdown exactly matches wrapper visible-report stdout.
- Controlled export stdout is CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.
- Controlled export stderr is empty.
- Rejected export without --visible-report-markdown writes nothing.
- Rejected outside-root export writes nothing.
- Rejected non-.md export writes nothing.
- Controlled fixture remains byte-for-byte unchanged.
- Fixture support files remain present.
- Temporary export root is removed by the QA test.
- No root report artifacts are created.

## Allowed scope

- Add this QA document.
- Add one QA unit test.
- Use subprocess.run only inside this QA test.
- Use shell=False only.
- Use cwd set to repository root.
- Use sys.executable to execute the wrapper.
- Use tests/tmp/local_media_agent/controlled_visible_report_exports as temporary controlled export root.
- Create and remove temporary controlled Markdown exports inside the controlled export root.
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

- New controlled Markdown export wrapper smoke execution QA test passes.
- Related wrapper smoke, implementation QA, implementation, wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this QA document and QA unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export wrapper smoke execution QA gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-wrapper-smoke-execution-qa-gate-v1-20260701
