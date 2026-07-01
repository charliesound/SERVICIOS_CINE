# CID Local Media Agent — Read-Only Single-File Metadata CLI Readiness Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.READINESS.GATE.V1`

## Result token

`LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_READINESS_GATE_V1_CLOSED`

## Gate type

`CLI_READINESS_ONLY_NOT_IMPLEMENTATION`

## Decision

`READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTRACT_GATE_WITH_ISOLATED_ENTRYPOINT_BOUNDARIES`

## Scope

This gate authorizes only a later CLI contract gate. It does not add a new command, does not change packaging, and does not expose a product CLI yet.

The already audited implementation remains isolated at:

`scripts/local_media_agent/read_only_single_file_metadata.py`

The only controlled target for the future CLI remains:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`

Expected controlled fixture identity:

- bytes: `239`
- sha256: `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`

## Future CLI boundary

The later CLI contract may describe an isolated operator-facing entrypoint, but this readiness gate does not implement that entrypoint.

Future entrypoint placeholder:

`cid-local-media-agent-read-only-single-file-metadata`

Allowed future CLI arguments:

- `--target-path`
- `--fixture-root`
- `--expected-sha256`
- `--expected-bytes`
- `--allowed-relative-path`
- `--result-json`

Allowed future output modes:

- JSON result payload for machine verification.
- Plain status output for operator smoke checks.

Allowed future exit codes:

- `0` for `CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK`.
- `2` for deterministic rejected outcomes.

## Mandatory privacy requirements

Future CLI output must preserve the redaction contract:

`<CONTROLLED_FIXTURE_ROOT>/media/controlled_plain_text_marker.txt`

It must never expose host-private absolute paths in success or rejection payloads.

## Explicit non-goals

The following remain forbidden in this gate and in the immediately following CLI contract gate unless a later explicit phase changes scope:

- no pyproject modification
- no product CLI integration
- no console script registration
- no scanner
- no batch processing
- no recursion
- no external media tool execution
- no ffprobe execution
- no ffmpeg execution
- no customer material
- no real media ingest
- no service backend
- no database access
- no frontend
- no installer
- no fixture modification

## Readiness checklist

This gate is acceptable only if all items are true:

1. The implementation QA gate is already closed.
2. The implementation remains Python-standard-library-only.
3. The future CLI boundary remains one controlled file only.
4. The future CLI contract does not register a product command yet.
5. The future CLI contract does not modify packaging configuration.
6. The future CLI contract preserves redacted paths.
7. The future CLI contract keeps deterministic rejection semantics.
8. The future CLI contract keeps external media tools forbidden.
9. The future CLI contract keeps scanner behavior forbidden.
10. The future CLI contract keeps batch and recursion forbidden.
11. The future CLI contract keeps customer material forbidden.
12. The future CLI contract may only prepare, not implement, the next entrypoint.

## Acceptance

`CLI_READINESS_PASS_FOR_SEPARATE_CONTRACT_GATE_ONLY`

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTRACT.GATE.V1`
