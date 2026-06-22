# CID Local Agent - FFprobe Controlled File Metadata Visible Report Renderer Implementation Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.V1`

## Objective

Define how a future runtime renderer implementation should behave when converting already-safe controlled ffprobe metadata JSON into a visible human-readable report.

This is not the runtime implementation.

This is only the implementation contract.

No runtime renderer is implemented.

No runtime scripts are modified.

## Source Stable State

HEAD:

`4993c1a60fcb9b746a69680bdfada43cfe730f8d`

## Source Phase

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1`

Source renderer contract files:

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract.py`
- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_qa_gate.py`

## Intended Future Renderer Function Contract

The future implementation should expose a deterministic local function equivalent to:

```python
render_controlled_ffprobe_metadata_visible_report(payload) -> str
```

The function must accept only already-safe controlled metadata payloads and return plain text or Markdown-safe text.

The function must not perform filesystem scanning, media probing, media processing, network calls, database writes, or runtime side effects.

## Input Payload Contract

The future implementation must require:

- input payload is an already-safe controlled metadata payload
- `input_policy` equals `controlled_fixture_only`
- `input_path_redacted` is filename-only
- full local paths are blocked or replaced with a safe placeholder
- `ffprobe_command_kind` equals `metadata_json`
- `metadata.format` may be null or object
- `metadata.streams` must be a list
- blocked flags remain false

## Output Report Contract

The future implementation must render a deterministic report with:

- title
- phase
- input policy
- redacted input filename
- preflight result
- format summary
- stream summary
- video stream summary
- audio stream summary
- safety boundary summary
- blocked operations summary
- human review required note
- next safe phase

The output must never claim media processing, scanner execution, audio extraction, sync, transcription, subtitles, timeline export, SaaS upload, DB write, installer creation, client-facing readiness, public demo readiness, sales demo readiness, or production readiness.

## Deterministic Rendering Rules

Rendering must be deterministic for the same payload.

The future implementation must use stable section ordering, stable labels, stable summary wording, and no timestamps, random values, hostnames, absolute paths, environment values, or runtime-specific identifiers.

## Safe Failure Behavior

Failed payloads must render safe failure reports, not exceptions leaking private data.

Failure reports must include a safe failure reason when available, unavailable summaries when metadata is absent, blocked operations, human review, and the next safe phase.

## Full Path Redaction Behavior

Full local paths must never be emitted.

The future implementation must use only `input_path_redacted` after forcing filename-only behavior.

If a full path is supplied in any visible filename field, the future implementation must reduce it to a safe basename or replace it with `redacted-input`.

## Invalid Input Policy Behavior

If `input_policy` is not `controlled_fixture_only`, the future implementation must produce a safe blocked report.

The blocked report must not include metadata internals, full paths, private details, scanner output, media processing output, SaaS identifiers, DB identifiers, or readiness claims.

## Null Format Behavior

When `metadata.format` is null, the future implementation must render a safe unavailable format summary.

## Empty Streams Behavior

When `metadata.streams` is empty, the future implementation must render a safe no-streams summary.

## Unknown Stream Behavior

Unknown stream types must be summarized safely as unknown stream entries.

Unknown streams must not trigger exceptions or path leakage.

## Blocked Operation Flags Expectation

The future implementation must require these flags to remain false:

- `media_processing_performed`
- `scanner_executed`
- `real_media_used`
- `ffmpeg_used`
- `audio_extraction_performed`
- `sync_generated`
- `transcription_generated`
- `subtitles_generated`
- `timeline_export_generated`
- `database_write`
- `saas_upload`
- `network_call`

If any blocked flag is true, the future implementation must produce a safe blocked report.

## Explicit Non-Authorization Boundaries

This contract does not authorize:

- runtime renderer implementation
- real rodaje material
- real media files
- arbitrary folders
- scanner execution
- ffprobe execution on real media
- ffmpeg media processing
- audio extraction
- sync generation
- transcription generation
- subtitle generation
- timeline export
- SaaS upload
- DB write
- installer creation
- client-facing readiness
- public demo readiness
- sales demo readiness
- production readiness

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.QA.GATE.V1`
