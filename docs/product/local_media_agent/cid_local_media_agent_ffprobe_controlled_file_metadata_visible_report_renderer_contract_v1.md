# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.V1`

## Objective

This phase defines a renderer contract for a future local renderer that converts already-safe controlled ffprobe metadata JSON into a visible human-readable report.

This is renderer contract only.

No runtime renderer is implemented.

No runtime scripts are modified.

## Source Stable State

HEAD:

`33d9d63cfd9cdea32f19cdfc8830a5796aec28fe`

## Source Phase

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1`

Source contract files:

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract.py`
- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate.py`

## Required Input Payload Contract

The future renderer must accept only already-safe controlled metadata payloads.

The future renderer must require:

- `input_policy` equal to `controlled_fixture_only`
- `input_path_redacted` as filename only
- no full local path emitted or rendered
- `ffprobe_command_kind` equal to `metadata_json`
- `metadata.format` as null or object
- `metadata.streams` as a list
- all safety flags remaining false

Payloads with `input_policy` not equal to `controlled_fixture_only` must be rejected or rendered only as a safe blocked report.

## Required Output Sections

The future renderer must render:

1. Report title
2. Phase
3. Input policy
4. Redacted input filename
5. Preflight result
6. Format summary
7. Stream summary
8. Video stream summary
9. Audio stream summary
10. Safety boundary summary
11. Blocked operations summary
12. Human review required note
13. Next safe phase

The future renderer must preserve safe output when `metadata.format` is null.

The future renderer must preserve safe output when `metadata.streams` is empty.

## Blocked Output Content

The future renderer must never include:

- full local paths
- real rodaje material references
- raw private file locations
- scanner output
- ffmpeg processing output
- audio extraction output
- sync output
- transcription output
- subtitle output
- timeline output
- SaaS identifiers
- DB identifiers
- installer claims
- client-facing claims
- public demo claims
- sales demo claims
- production readiness claims

## Safety Flags Expectation

The future renderer must treat these flags as false-only for this contract:

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

If any safety flag is true, the future renderer must reject the payload or emit only a safe blocked report without private details or full paths.

## Failure-Mode Behavior

Failure payloads must still render a safe and useful report.

Failure reports must include:

- report title
- phase
- input policy
- redacted input filename when available
- preflight result
- safe failure reason when available
- unavailable format summary when `metadata.format` is null
- zero-stream summary when `metadata.streams` is empty
- safety boundary summary
- blocked operations summary
- human review required note
- next safe phase

## Explicit Non-Authorization Boundaries

This contract does not authorize:

- real media
- real rodaje material
- arbitrary folders
- scanner execution
- ffmpeg media processing
- audio extraction
- sync generation
- transcription generation
- subtitle generation
- timeline export
- SaaS upload
- database write
- installer creation
- client-facing use
- public demo
- sales demo
- production use

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CONTRACT_PASS_READY_FOR_QA_GATE`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1`
