# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Implementation Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.IMPLEMENTATION.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_IMPLEMENTATION_GATE_V1_CLOSED

## Purpose

Controlled implementation gate for Markdown visible report export.

This phase implements the future reserved output flag as a controlled export path accepted by the implementation parser. The implementation writes Markdown only inside the controlled test output root and only when the visible report mode is explicitly requested.

## Current stable base

Base HEAD: 53ad71047f39ca0c928460263a4a1b9bf1538f59

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-readiness-gate-v1-20260701

## Implemented capability

--visible-report-output

## Required companion mode

--visible-report-markdown

## Controlled output root

tests/tmp/local_media_agent/controlled_visible_report_exports

## Modified implementation file

scripts/local_media_agent/read_only_single_file_metadata.py

## Wrapper file that must remain unchanged

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Implementation behavior

The implementation must:

- Accept the controlled output path flag.
- Keep the wrapper as a delegating layer.
- Require --visible-report-markdown when the controlled output path flag is used.
- Reject output paths outside tests/tmp/local_media_agent/controlled_visible_report_exports.
- Reject missing parent directories.
- Reject symlink parent directories.
- Reject symlink output files.
- Reject output paths inside tests/fixtures.
- Reject output paths inside the controlled fixture root.
- Reject output paths at repository root.
- Reject Windows-style path strings inside WSL.
- Reject non-.md suffixes.
- Reject overwrite by default.
- Write UTF-8 Markdown only.
- Write exactly the same Markdown that --visible-report-markdown emits to stdout.
- Keep default status output unchanged.
- Keep --result-json output unchanged.
- Keep --visible-report-markdown stdout-only behavior unchanged when no output path is provided.
- Preserve exit code 0 for accepted metadata and valid export.
- Preserve exit code 2 for rejected metadata or rejected output policy.
- Leave no export file behind on rejected policy.
- Preserve controlled fixture bytes and SHA256.
- Keep pyproject unchanged.
- Keep the wrapper unchanged.

## Forbidden scope

- No wrapper behavior changes.
- No renderer behavior changes.
- No in-memory integration behavior changes.
- No overwrite flag.
- No export outside controlled output root.
- No export into tests/fixtures.
- No export into fixture source tree.
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

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New controlled Markdown export implementation test passes.
- Related wrapper smoke QA, wrapper smoke execution, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only the implementation file, this implementation document, and this implementation unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

feat: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export implementation gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-implementation-gate-v1-20260701
