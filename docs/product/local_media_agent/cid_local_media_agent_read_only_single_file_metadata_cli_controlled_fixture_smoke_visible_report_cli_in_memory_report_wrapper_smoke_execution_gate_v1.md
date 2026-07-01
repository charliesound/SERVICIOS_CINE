# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI In-memory Report Wrapper Smoke Execution Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED

## Purpose

Doc/test-only controlled smoke execution gate for the public isolated CLI wrapper.

This phase executes scripts/local_media_agent/read_only_single_file_metadata_cli.py through the Python interpreter with fixed arguments against the controlled non-customer fixture only. It validates that --visible-report-markdown works through the wrapper, emits Markdown to stdout, preserves deterministic exit codes, keeps stderr empty, and does not generate report files.

## Current stable base

Base HEAD: 5f10e075d64146be5a2c9d8959ffeb6ddbe67ac8

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-implementation-qa-gate-v1-20260701

## Executed wrapper artifact

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Audited implementation artifact

scripts/local_media_agent/read_only_single_file_metadata.py

## Existing in-memory integration artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py

## Existing renderer artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Prior audited chain

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py

## Existing controlled fixture support files

The controlled fixture already contains README.md and manifest.controlled.json as baseline fixture support files. These are not generated report artifacts and must remain unchanged.

## Controlled execution mode

The QA test may use subprocess.run only to execute the Python wrapper script with:

- sys.executable
- shell=False
- capture_output=True
- text=True
- timeout
- cwd set to repository root
- controlled fixture paths only
- no real or customer material

This permission is limited to the QA test for this wrapper smoke execution gate. It does not permit subprocess usage in production implementation code.

## CLI mode under smoke execution

--visible-report-markdown

## Regression modes under smoke execution

- default status output
- --result-json output
- --visible-report-markdown output
- rejected metadata exit code

## Controlled fixture identity

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Smoke execution requirements

The wrapper smoke execution test must verify:

- The wrapper exists and is Python parseable.
- The wrapper still delegates to implementation.run_cli(argv).
- The wrapper itself does not define ArgumentParser.
- The wrapper itself does not implement --visible-report-markdown.
- The implementation parser exposes --visible-report-markdown.
- Default wrapper execution returns exit code 0 and exact status stdout.
- Default wrapper execution leaves stderr empty.
- --result-json wrapper execution returns exit code 0 and valid JSON stdout.
- --result-json wrapper execution does not include Markdown.
- --visible-report-markdown wrapper execution returns exit code 0 and Markdown stdout.
- --visible-report-markdown wrapper execution leaves stderr empty.
- Rejected --visible-report-markdown wrapper execution returns exit code 2 and Markdown stdout with FAIL.
- Controlled fixture byte size and SHA256 remain unchanged.
- The fixture tree is unchanged before and after smoke execution.
- No report file is created in the repository root or controlled fixture tree.
- No export behavior is introduced.
- No persistent output path is introduced.
- No pyproject console script registration is introduced.

## Allowed scope

- Add this smoke execution document.
- Add one smoke execution unit test.
- Execute the wrapper only from the test with controlled fixture arguments.
- Use subprocess.run only inside the QA test and only with shell=False.
- Capture stdout and stderr in memory.
- Verify no file generation.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New wrapper smoke execution test passes.
- Related implementation QA, implementation, readiness, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this smoke execution document and smoke execution unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke visible report wrapper smoke execution gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-wrapper-smoke-execution-gate-v1-20260701
