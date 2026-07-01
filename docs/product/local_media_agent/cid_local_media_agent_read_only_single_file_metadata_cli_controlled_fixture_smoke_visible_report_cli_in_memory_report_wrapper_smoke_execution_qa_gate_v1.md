# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI In-memory Report Wrapper Smoke Execution QA Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.QA.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_WRAPPER_SMOKE_EXECUTION_QA_GATE_V1_CLOSED

## Purpose

Doc/test-only QA gate for the controlled smoke execution of the public isolated wrapper.

This phase audits the previously closed wrapper smoke execution gate. It verifies that the wrapper smoke execution remains controlled, reproducible, limited to the controlled non-customer fixture, shell-free, artifact-free, and separated from production implementation changes.

## Current stable base

Base HEAD: 849eaa7b65a0e1f26c88ddf5a79f6d08cf78ee4f

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-wrapper-smoke-execution-gate-v1-20260701

## Audited closed phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1

## Audited smoke execution result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED

## Audited smoke execution artifacts

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py

## Audited wrapper artifact

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Audited implementation artifact

scripts/local_media_agent/read_only_single_file_metadata.py

## Existing in-memory integration artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py

## Existing renderer artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## CLI mode audited

--visible-report-markdown

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

- The previous wrapper smoke execution document exists.
- The previous wrapper smoke execution test exists.
- The previous wrapper smoke execution document declares doc/test-only scope.
- The previous wrapper smoke execution document permits subprocess.run only inside the QA test.
- The previous wrapper smoke execution document requires sys.executable.
- The previous wrapper smoke execution document requires shell=False.
- The previous wrapper smoke execution document requires fixed controlled fixture paths.
- The previous wrapper smoke execution document forbids real and customer material.
- The previous wrapper smoke execution document forbids report file generation.
- The previous wrapper smoke execution test is Python parseable.
- The previous wrapper smoke execution test uses subprocess.run.
- The previous wrapper smoke execution test uses sys.executable.
- The previous wrapper smoke execution test uses shell=False.
- The previous wrapper smoke execution test uses capture_output=True.
- The previous wrapper smoke execution test uses text=True.
- The previous wrapper smoke execution test sets cwd to repository root.
- The previous wrapper smoke execution test has a timeout.
- The previous wrapper smoke execution test verifies default status output.
- The previous wrapper smoke execution test verifies --result-json output.
- The previous wrapper smoke execution test verifies --visible-report-markdown output.
- The previous wrapper smoke execution test verifies rejected visible report exit code 2.
- The previous wrapper smoke execution test verifies stderr is empty.
- The previous wrapper smoke execution test verifies fixture tree snapshots before and after execution.
- The previous wrapper smoke execution test verifies root report artifacts do not change.
- The previous wrapper smoke execution test allows existing README.md and manifest.controlled.json fixture support files.
- The wrapper remains a thin delegating layer.
- The implementation parser still exposes --visible-report-markdown and --result-json.
- The controlled fixture remains byte-for-byte unchanged.
- pyproject does not register a console script for this mode.

## Allowed scope

- Add this QA document.
- Add one QA unit test.
- Audit the previously closed wrapper smoke execution gate.
- Optionally execute the wrapper again only from the QA test with controlled fixture arguments.
- Capture stdout and stderr in memory.
- Verify no artifact creation.
- Verify controlled fixture integrity.
- Keep this phase doc/test-only.

## Forbidden scope

- No implementation behavior changes.
- No wrapper behavior changes.
- No renderer behavior changes.
- No in-memory integration behavior changes.
- No report file generation.
- No export behavior.
- No persistent output path.
- No new smoke scenario outside controlled fixture.
- No shell=True.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New wrapper smoke execution QA test passes.
- Related wrapper smoke execution, implementation QA, implementation, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this QA document and QA unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke visible report wrapper smoke execution QA gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-wrapper-smoke-execution-qa-gate-v1-20260701
