# CID Local Media Agent Slice 3 G002 Contract

## Purpose

G002 adds one supported CLI entrypoint for the already published same-run local media pilot flow. The command composes `run_pilot_flow` and the public pilot browse/search handoff without changing either semantic module.

## CLI Invocation

```text
cid pilot OPERATION --input-root ROOT --selected-media MEDIA --asset-id ASSET_ID --model-local-path MODEL [OPTIONS]
```

Operations are exactly `browse` and `search`.

Required arguments:

- `OPERATION`: `browse` or `search`.
- `--input-root ROOT`.
- `--selected-media MEDIA`.
- `--asset-id ASSET_ID`.
- `--model-local-path MODEL`.

Optional arguments:

- `--language-hint LANG`.
- `--device cpu|cuda`, default `cpu`.
- `--ffmpeg-path PATH`.
- `--temp-dir PATH`.
- `--offset NON_NEGATIVE_INTEGER`, browse only, default `0`.
- `--limit POSITIVE_INTEGER`, default `20`, bounded by the existing operation maximum of `100`.
- `--query QUERY`, search only and required for `search` after stripping whitespace.

`browse` rejects `--query` and `search` rejects `--offset`. No other operation, alias, persistence, or reload option is accepted.

## Direct Handoff

The command constructs `PilotFlowRequest` and calls `scripts.local_media_agent.pilot_flow.run_pilot_flow` exactly once. Only a result with status `PILOT_FLOW_COMPLETED` enters `scripts.local_media_agent.pilot_browse_search_handoff.handoff_pilot_transcript_segments`.

The result remains in memory. G002 does not require user Python glue, manual JSON reshaping, a rescan, retranscription, or durable reload. Existing `_transcript_payload` serialization remains the output boundary, including the existing additive `source_moment` descriptor.

## Output And Exit Codes

- Success writes the existing JSON object containing `operation`, `result_limit_maximum`, and `results` to stdout, with stderr empty, and exits `0`.
- Invalid CLI arguments, invalid operation, invalid numeric bounds, invalid operation-specific options, empty search query, and handoff validation failures write `CID_CLI_ARGUMENTS_REJECTED` to stderr and exit `2`.
- A returned pilot failure, including output-integrity failure, is written as its sanitized JSON payload to stdout and exits `1`; it never enters handoff.
- Unexpected exceptions write `CID_CLI_INTERNAL_FAILURE` to stderr and exit `1`.
- No raw traceback, internal stack location, repository path, or environment path is emitted.
- A search with no matches is successful and returns `results: []` with exit `0`.

## Traceability

The existing browse projection preserves, when present, `asset_id`, `segment_ref`, `segment_index`, original `text`, `source_start_seconds`, `source_end_seconds`, and `source_timecode`. The existing CLI serializer also preserves the additive source-moment metadata.

The browse projection does not expose STT timing or the full provenance dictionary. G002 does not fabricate, reconstruct, or add those fields.

## Privacy And Scope

- Processing remains local-only.
- Source media remains read-only.
- No network, provider, database, cloud persistence, telemetry, or new dependency is added.
- No transcript store, transcript cache, reload, or multi-session resume is added.
- GAP-008 is explicitly excluded.

## Frozen Modules

These modules are unchanged and remain semantic contract authorities:

- `scripts/local_media_agent/pilot_flow.py`
- `scripts/local_media_agent/transcript_browse.py`
- `scripts/local_media_agent/source_moment_navigation.py`
- `scripts/local_media_agent/pilot_browse_search_handoff.py`

## Implementation Paths

Only these paths belong to G002:

- `scripts/local_media_agent/cid_cli.py`
- `tests/unit/test_cid_local_media_agent_pilot_browse_search_handoff_contract.py`
- `docs/product/local_media_agent/cid_local_media_agent_slice3_pilot_flow_cli_handoff_continuity_contract_v1.md`

No new source or test file is added.

## Required Scenarios

| Scenario | Contract assertion |
|---|---|
| `CLI_COMMAND_HELP_VISIBLE` | `cid pilot --help` exposes the frozen command and options. |
| `CLI_VALID_PILOT_REQUEST_ORCHESTRATED` | The command constructs the published request and invokes the pilot boundary. |
| `PILOT_FAILURE_BLOCKS_HANDOFF` | A non-success pilot result never reaches handoff. |
| `OUTPUT_INTEGRITY_FAILURE_BLOCKS_HANDOFF` | Output-preflight failure is a non-success CLI result. |
| `VALIDATED_PILOT_RESULT_PASSED_DIRECTLY_TO_HANDOFF` | The exact in-memory pilot mapping reaches the public handoff. |
| `BROWSE_USER_REACHABLE` | `pilot browse` returns the existing browse projection. |
| `SEARCH_USER_REACHABLE` | `pilot search` returns the existing search projection. |
| `SEARCH_QUERY_PRESERVED` | Search query and operation semantics are preserved. |
| `SEARCH_RESULT_TRACEABILITY_PRESERVED` | Existing identity, text, timing, and timecode fields remain present. |
| `NO_RESCAN` | The pilot command does not invoke the standalone scanner CLI. |
| `NO_RETRANSCRIPTION` | The CLI invokes the pilot boundary once and does not repeat it. |
| `NO_MANUAL_JSON` | The same-run path creates no intermediate transcript file. |
| `NO_DURABLE_RELOAD` | The pilot path does not call transcript reload. |
| `SANITIZED_FAILURE_OUTPUT` | Returned failures contain sanitized codes rather than raw internals. |
| `NO_RAW_TRACEBACK` | Unexpected exceptions expose only the existing internal-failure token. |
| `EXISTING_CLI_COMMANDS_BACKWARD_COMPATIBLE` | Existing help and transcript behavior remain usable. |
| `GAP008_REMAINS_ABSENT` | Reload/persistence options are not accepted or implemented. |

All scenarios use synthetic fixtures, mocks, or monkeypatching. No scenario invokes real media, FFmpeg, ffprobe, transcription, providers, network, database, or runtime CLI processes.

## Test Command

The single implementation-gate command is:

```bash
PYTHONPATH=src pytest -q tests/unit/test_cid_local_media_agent_pilot_browse_search_handoff_contract.py tests/unit/test_cid_local_media_agent_pilot_flow_contract.py tests/unit/test_cid_local_media_agent_transcript_browse_contract.py tests/unit/test_cid_local_media_agent_source_moment_navigation_contract.py
```

## Out Of Scope

G002 does not modify the pilot flow, transcript segment schema, browse/search schema, source-moment schema, or handoff schema. It does not implement GAP-008, durable persistence, reload, semantic retrieval, external-player launching, NLE integration, frontend work, backend SaaS work, database work, provider integration, installer work, or dependency changes.
