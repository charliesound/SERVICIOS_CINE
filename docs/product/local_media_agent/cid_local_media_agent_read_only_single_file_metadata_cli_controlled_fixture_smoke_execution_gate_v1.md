# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Execution Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.EXECUTION.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_EXECUTION_GATE_V1_CLOSED

## Purpose

Controlled smoke execution gate for the isolated read-only single-file metadata CLI against the controlled non-customer fixture.

This phase validates that the CLI can run end-to-end against the approved controlled fixture and return visible auditable JSON without writing files or crossing integration boundaries.

## Current stable base

Base HEAD: 58c2d1d2519d5cab4e832d4e62110eccd8d351fd

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-readiness-gate-v1-20260701

## Audited CLI command shape

python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path TARGET_PATH --fixture-root FIXTURE_ROOT --expected-sha256 EXPECTED_SHA256 --expected-bytes EXPECTED_BYTES --allowed-relative-path ALLOWED_RELATIVE_PATH --result-json

## Controlled fixture

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Allowed scope

- Add this smoke execution document.
- Add one smoke execution unit test.
- Execute the existing CLI main function from test with explicit argv.
- Capture stdout and stderr in memory.
- Validate visible JSON smoke result.
- Validate fixture integrity before execution.
- Keep execution limited to the controlled non-customer fixture.

## Forbidden scope

- No CLI behavior changes.
- No subprocess.
- No shell execution.
- No fixture modification.
- No output file creation.
- No batch processing.
- No recursive traversal.
- No scanner integration.
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

## Smoke execution assertions

The smoke test must verify:

- The controlled fixture exists.
- The controlled fixture byte size matches 239.
- The controlled fixture SHA256 matches the expected value.
- The isolated CLI exposes a callable main function.
- The CLI smoke execution returns exit code 0.
- The CLI smoke execution emits non-empty stdout.
- The CLI smoke execution emits valid JSON when --result-json is used.
- The JSON smoke result contains the expected fixture filename, byte size, and SHA256.
- The smoke execution does not create or modify files.
- pyproject does not register the CLI as a console script.

## Required validation commands

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_readiness_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New smoke execution test passes.
- Related readiness and implementation chain tests pass.
- Mandatory guards pass.
- Only this smoke execution document and smoke execution unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke execution gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-execution-gate-v1-20260701
