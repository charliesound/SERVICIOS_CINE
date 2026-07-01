# CID Local Media Agent — Read-Only Single-File Metadata CLI Implementation Readiness Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.READINESS.GATE.V1`

## Result token

`LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_READINESS_GATE_V1_CLOSED`

## Status

`READY_FOR_REVIEW`

## Decision frozen by this gate

`READY_FOR_SEPARATE_ISOLATED_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_GATE_WITHOUT_PYPROJECT_REGISTRATION`

## Purpose

This gate confirms that the audited read-only single-file metadata implementation and the isolated CLI contract are ready for a later, separate CLI implementation gate.

This phase is documentation and test only. It must not create the CLI file, register a console script, modify packaging, modify fixtures, execute media tooling, or expand scanner/runtime behavior.

## Baseline dependencies

Required closed predecessors:

- `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.QA.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.READINESS.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTRACT.GATE.V1`

Required existing implementation:

- `scripts/local_media_agent/read_only_single_file_metadata.py`

Required future isolated entrypoint name:

- `cid-local-media-agent-read-only-single-file-metadata`

Required future implementation file, not created by this gate:

- `scripts/local_media_agent/read_only_single_file_metadata_cli.py`

## Allowed future implementation scope

The later CLI implementation gate may add only an isolated script under `scripts/local_media_agent/` that delegates to the already audited Python-standard-library implementation.

Allowed future CLI arguments remain exactly:

- `--target-path`
- `--fixture-root`
- `--expected-sha256`
- `--expected-bytes`
- `--result-json`

Allowed future success behavior:

- JSON output when `--result-json` is present.
- Plain output `READ_ONLY_SINGLE_FILE_METADATA_COLLECTED` when `--result-json` is absent.
- Exit code `0` for success.
- Exit code `2` for deterministic validation rejection.

## Required target fixture boundary

The future CLI implementation must remain limited to the controlled fixture pack:

- `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`
- expected bytes: `239`
- expected SHA256: `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`

## Mandatory prohibitions for this gate

This gate must not:

- create `scripts/local_media_agent/read_only_single_file_metadata_cli.py`
- modify `scripts/local_media_agent/read_only_single_file_metadata.py`
- modify `pyproject.toml`
- register console scripts
- create installation metadata
- create batch behavior
- create recursive traversal
- create scanner behavior
- call external media tools
- read real material
- read customer material
- modify fixture files
- touch SaaS, database, backend, frontend, installer, Docker, Alembic, Stripe, credits, ledger, or AI Jobs

## Mandatory prohibitions for the later isolated CLI implementation

The later CLI implementation must still not:

- modify `pyproject.toml`
- register a package entrypoint
- scan folders
- recurse
- process batches
- call external media tools
- touch real or customer material
- write output files
- send data over network
- touch SaaS/database/backend/frontend/installer surfaces

## Acceptance checklist

The gate is acceptable only if all items are true:

- The implementation script already exists and remains unchanged by this gate.
- The CLI contract gate exists.
- The future entrypoint name is documented but not registered.
- The future CLI implementation file is documented but not created.
- The fixture boundary is explicit and unchanged.
- Deterministic success and rejection behavior is documented.
- Private path redaction remains mandatory.
- No batch, recursion, scanner, external media tooling, product packaging, or SaaS/database changes are authorized.

## Closure statement

When this gate closes, the only authorized next step is a separate isolated CLI implementation gate with strict file scope and no packaging registration.
