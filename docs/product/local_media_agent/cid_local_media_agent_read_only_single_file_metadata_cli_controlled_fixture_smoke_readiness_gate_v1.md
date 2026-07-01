# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Readiness Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.READINESS.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_READINESS_GATE_V1_CLOSED

## Purpose

Doc/test-only readiness gate for a future controlled smoke execution of the isolated read-only single-file metadata CLI against the controlled non-customer fixture.

This phase does not execute the CLI as a product smoke yet. It prepares and audits the readiness conditions required before a later controlled smoke gate may run.

## Current stable base

Base HEAD: a68448bafd0e837c90cedbfa46d4b464acaf2527

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-implementation-qa-gate-correction-v1-20260701

## Audited CLI

scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Controlled fixture

Path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

## Allowed scope

- Add this readiness document.
- Add one readiness unit test.
- Audit that the isolated CLI exists.
- Audit that the controlled fixture exists and remains unchanged.
- Define future smoke readiness conditions.
- Keep the phase doc/test-only.

## Forbidden scope

- No CLI behavior changes.
- No product smoke execution in this phase.
- No fixture modification.
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

## Future smoke gate readiness conditions

A later controlled smoke gate may only run if:

- The input is exactly the controlled non-customer fixture declared in this document.
- The fixture byte size and SHA256 match the expected values.
- The CLI remains isolated under scripts/local_media_agent.
- The CLI remains read-only.
- The smoke command does not use scanner, batch, recursion, FFmpeg, ffprobe, SaaS, database, backend, frontend, installer, Docker, Alembic, Stripe, AI Jobs, credits, ledger, real material, or customer material.
- The future smoke result is visible and auditable.
- Any output, if introduced later, must be controlled and explicitly scoped by a later phase.

## Required validation commands

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_readiness_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New readiness test passes.
- Related chain tests pass.
- Mandatory guards pass.
- Only this readiness document and readiness unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled fixture smoke readiness gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-readiness-gate-v1-20260701
