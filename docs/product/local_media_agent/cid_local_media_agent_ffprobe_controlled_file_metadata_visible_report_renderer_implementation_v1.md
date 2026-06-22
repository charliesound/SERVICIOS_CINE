# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.V1`

## Objective

Implement a pure local renderer for already-safe controlled ffprobe metadata payloads.

The renderer converts a controlled metadata payload into deterministic plain text or Markdown-safe text.

It does not create a CLI, read media files, scan folders, call subprocesses, execute ffprobe, execute ffmpeg, write files, call a network, or write to a database.

## Source Stable State

HEAD:

`06e2b921ead7408ec4a6aaa6ffd330a1e616ebe7`

## Source Phase

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.QA.GATE.V1`

Source contract QA gate:

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_qa_gate.py`

## Runtime API

```python
render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str
```

Runtime file:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

## Input Payload Contract

The renderer accepts only already-safe controlled metadata payloads.

The payload must provide:

- `input_policy` equal to `controlled_fixture_only`
- `ffprobe_command_kind` equal to `metadata_json`
- `input_path_redacted` as filename-only text
- `metadata.format` as null or object
- `metadata.streams` as a list
- blocked operation flags set to false

## Output Report Sections

The renderer output includes:

- CID Local Media Agent - Controlled FFprobe Metadata Visible Report
- Phase
- Input Policy
- Input
- Preflight Result
- Format Summary
- Stream Summary
- Video Streams
- Audio Streams
- Safety Boundary
- Blocked Operations
- Human Review Required
- Next Safe Phase

## Safe Blocked Report Behavior

Invalid controlled metadata payloads produce a safe blocked report.

Blocked reports do not render metadata internals and do not expose full local paths.

## Full Path Redaction Behavior

The renderer uses `input_path_redacted` only.

If `input_path_redacted` contains path separators, Windows path markers, UNC markers, relative traversal, or shell-home markers, the renderer emits `<redacted-input>`.

Full paths inside metadata fields are not emitted.

## Invalid Input Policy Behavior

If `input_policy` is not `controlled_fixture_only`, the renderer emits a safe blocked report.

## Invalid FFprobe Command Kind Behavior

If `ffprobe_command_kind` is not `metadata_json`, the renderer emits a safe blocked report.

## Null Format Behavior

If `metadata.format` is null or not an object, the renderer emits `format unavailable`.

## Empty Streams Behavior

If `metadata.streams` is empty or invalid, the renderer emits no-stream summaries.

## Unknown Stream Behavior

Unknown stream types are summarized as unknown streams without raising exceptions.

## Explicit Non-Authorization Boundaries

This implementation does not authorize:

- real rodaje material
- real media files
- folder scanning
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

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_PASS_READY_FOR_QA_GATE`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.QA.GATE.V1`
