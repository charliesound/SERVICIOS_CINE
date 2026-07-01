# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Contract QA Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.QA.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTRACT_QA_GATE_V1_CLOSED

## Purpose

Doc/test-only QA gate for the controlled Markdown export contract.

This phase audits the previously closed controlled Markdown export contract. It verifies that the future --visible-report-output mode remains contract-only, that no implementation or parser change exists yet, and that the current CLI behavior remains unchanged.

## Current stable base

Base HEAD: 760b37939fac7b9ec95755b8eae178494f671689

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-contract-v1-20260701

## Audited closed phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.V1

## Audited closed result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTRACT_V1_CLOSED

## Audited contract artifacts

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py

## Existing runtime artifacts under audit

- scripts/local_media_agent/read_only_single_file_metadata_cli.py
- scripts/local_media_agent/read_only_single_file_metadata.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Future reserved flag under QA

--visible-report-output

## Existing implemented visible report flag

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

- This QA document exists.
- The audited contract document exists.
- The audited contract test exists.
- The audited contract document declares the contract phase and result.
- The audited contract document declares --visible-report-output as future reserved only.
- The audited contract document declares --visible-report-markdown as already implemented.
- The audited contract document says the future export flag is not implemented in that phase.
- The audited contract document forbids parser changes in that phase.
- The audited contract document forbids CLI behavior changes in that phase.
- The audited contract document forbids report file generation in that phase.
- The audited contract document forbids export behavior in that phase.
- The audited contract document defines safe output root policy.
- The audited contract document requires rejecting fixture source tree paths.
- The audited contract document requires rejecting tests/fixtures paths.
- The audited contract document requires rejecting repository root output paths.
- The audited contract document requires rejecting Windows-style paths inside WSL.
- The audited contract document requires rejecting overwrite by default.
- The audited contract document requires .md suffix restriction.
- The audited contract test is Python parseable.
- The audited contract test verifies the existing parser does not expose --visible-report-output.
- The audited contract test verifies the existing wrapper does not expose --visible-report-output.
- The audited contract test verifies current status, JSON, and Markdown stdout behavior.
- The audited contract test verifies fixture integrity.
- The audited contract test avoids subprocess execution.
- The audited contract test avoids file writes.
- The existing implementation parser still does not expose --visible-report-output.
- The existing implementation parser still exposes --visible-report-markdown and --result-json.
- The wrapper remains a thin delegating layer.
- Current default status behavior remains unchanged.
- Current --result-json behavior remains unchanged.
- Current --visible-report-markdown behavior remains stdout-only.
- No root report artifacts are created by this QA phase.
- The controlled fixture remains byte-for-byte unchanged.
- pyproject does not register a console script for this future mode.

## Allowed scope

- Add this QA document.
- Add one QA unit test.
- Audit the previously closed controlled Markdown export contract.
- Execute current in-process CLI behavior only through run_cli in the QA test.
- Capture stdout in memory.
- Verify no artifact creation.
- Verify controlled fixture integrity.
- Keep this phase doc/test-only.

## Forbidden scope

- No implementation of --visible-report-output.
- No parser change.
- No CLI behavior change.
- No wrapper behavior change.
- No renderer behavior change.
- No in-memory integration behavior change.
- No report file generation.
- No export behavior.
- No filesystem writes except adding this QA document and QA test.
- No persistent output path.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New controlled Markdown export contract QA test passes.
- Related controlled Markdown export contract, wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this QA document and QA unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export contract QA gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-contract-qa-gate-v1-20260701
