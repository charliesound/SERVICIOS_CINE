# CID Local Media Agent — Read-Only Single-File Metadata CLI Implementation Gate V1

Phase: `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.GATE.V1`

Result token: `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_GATE_V1_CLOSED`

## Purpose

Add an isolated CLI wrapper for the already-audited read-only single-file metadata implementation.

## Added implementation file

`scripts/local_media_agent/read_only_single_file_metadata_cli.py`

The file provides an isolated `main(argv=None) -> int` entrypoint and delegates to `scripts/local_media_agent/read_only_single_file_metadata.py` without registering project-wide console scripts.

## Allowed behavior

- Python standard library only.
- One controlled fixture target only.
- Delegates to the audited `run_cli` function.
- Supports the existing contract arguments: `--target-path`, `--fixture-root`, `--expected-sha256`, `--expected-bytes`, `--result-json`.
- Preserves exit code `0` for success.
- Preserves exit code `2` for deterministic validation rejection.
- Preserves JSON and plain outputs from the audited implementation.

## Controlled fixture boundary

Target fixture: `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`

Expected bytes: `239`

Expected SHA256: `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`

## Explicit non-goals

- No project-wide CLI registration.
- No dependency metadata edits.
- No scanner behavior.
- No batch mode.
- No recursive traversal.
- No external media tool execution.
- No fixture modification.
- No product installer behavior.
- No service/backend/frontend changes.

## Acceptance criteria

- The isolated CLI file exists under `scripts/local_media_agent/`.
- The isolated CLI exposes `main`.
- The isolated CLI delegates to `run_cli` from the audited implementation.
- JSON success is parseable and does not expose private absolute paths.
- Plain success emits `CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK`.
- Deterministic rejections still return exit code `2`.
- The staged scope is exactly this doc, the isolated CLI wrapper, and the QA test.

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.QA.GATE.V1`
