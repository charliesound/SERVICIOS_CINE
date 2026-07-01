# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Contract V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTRACT_V1_CLOSED

## Purpose

Doc/test-only contract for a future controlled Markdown export mode for the visible report produced by the read-only single-file metadata CLI.

This phase defines the product and safety contract for a future explicit output flag. It does not implement that flag, does not change CLI behavior, does not change wrapper behavior, does not change renderer behavior, does not change in-memory integration behavior, and does not write report files.

## Current stable base

Base HEAD: b0fb9dd8dc8b42461e3a1924cd1916bdc28e086d

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-wrapper-smoke-execution-qa-gate-v1-20260701

## Future reserved CLI flag

--visible-report-output

## Existing implemented CLI flag

--visible-report-markdown

## Existing public wrapper artifact

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Existing implementation artifact

scripts/local_media_agent/read_only_single_file_metadata.py

## Existing in-memory integration artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py

## Existing renderer artifact

scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Prior closed chain

- CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.QA.GATE.V1
- CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1
- CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.IMPLEMENTATION.QA.GATE.V1
- CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.IMPLEMENTATION.GATE.V1
- CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.READINESS.GATE.V1

## Prior closed artifacts

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py
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

Existing baseline support files inside fixture:

- README.md
- manifest.controlled.json

These are baseline fixture support files, not generated report artifacts.

## Future controlled export contract

The future implementation of --visible-report-output must:

- Be explicit and opt-in.
- Require --visible-report-markdown or an equivalent explicit visible report mode.
- Accept one output path argument.
- Treat the output path as a file path, not a directory scan request.
- Resolve the output path safely before writing.
- Reject missing parent directories.
- Reject symlink output files.
- Reject symlink parent directories.
- Reject paths outside the future approved controlled output root.
- Reject paths that point inside the controlled fixture source tree.
- Reject paths that point inside tests/fixtures.
- Reject paths that point to the repository root directly.
- Reject absolute host-private paths unless explicitly inside the approved controlled output root.
- Reject Windows-style paths inside WSL.
- Reject overwrite by default.
- Require a future explicit overwrite flag before replacing an existing report file.
- Restrict the output suffix to .md.
- Write UTF-8 text only.
- Write exactly the Markdown returned by the existing in-memory visible report integration.
- Return a deterministic success result after writing.
- Return a deterministic rejection result without writing when policy fails.
- Keep default CLI status output unchanged.
- Keep --result-json behavior unchanged.
- Keep --visible-report-markdown stdout behavior unchanged when no output path is provided.
- Preserve accepted exit code 0.
- Preserve rejected exit code 2.
- Avoid report writes during metadata collection failures unless future policy explicitly allows failure report export.
- Never write media-derived absolute paths into the report.
- Preserve redacted paths only.
- Preserve controlled fixture identity.
- Preserve human review placeholders.
- Keep implementation local-only.
- Avoid network calls.
- Avoid database calls.
- Avoid scanner integration.
- Avoid batch processing.
- Avoid recursive traversal.

## Future output root policy

A future controlled export implementation must use a dedicated controlled output root, for example:

tests/tmp/local_media_agent/controlled_visible_report_exports

The exact output root may change in the future implementation phase, but the implementation must be covered by tests before use.

## Explicitly forbidden for this contract phase

- No implementation of --visible-report-output.
- No parser change.
- No CLI behavior change.
- No wrapper behavior change.
- No renderer behavior change.
- No in-memory integration behavior change.
- No report file generation.
- No export behavior.
- No filesystem writes except adding this contract document and test.
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

## Contract QA requirements

The contract test must verify:

- This contract document exists.
- This contract document declares the phase and expected result.
- This contract document declares --visible-report-output as future reserved only.
- This contract document declares --visible-report-markdown as already implemented.
- This contract document declares no implementation in this phase.
- Existing wrapper, implementation, integration, and renderer artifacts exist.
- Existing implementation parser does not expose --visible-report-output yet.
- Existing wrapper does not expose --visible-report-output.
- Existing implementation still exposes --visible-report-markdown.
- Existing implementation still exposes --result-json.
- Existing default behavior remains status-only.
- Existing --result-json behavior remains JSON-only.
- Existing --visible-report-markdown behavior remains stdout-only.
- Existing controlled fixture remains byte-for-byte unchanged.
- Existing fixture support files are recognized as baseline support files.
- No generated report artifacts are created by this contract phase.
- pyproject does not register a console script for this future mode.
- The contract explicitly forbids real and customer material.
- The contract explicitly forbids scanner, batch, recursive traversal, FFmpeg, ffprobe, database, backend, frontend, and SaaS work.

## Required validation commands

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New controlled Markdown export contract test passes.
- Related wrapper smoke QA, wrapper smoke execution, implementation QA, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this contract document and contract unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

docs: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export contract

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-contract-v1-20260701
