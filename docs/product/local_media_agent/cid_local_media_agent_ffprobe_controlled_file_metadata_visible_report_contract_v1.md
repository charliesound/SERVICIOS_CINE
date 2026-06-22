# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.V1`

## Objective

This phase defines a visible report contract for controlled ffprobe metadata preflight output.

It is only a visible report contract.

It does not implement runtime rendering yet.

It does not modify runtime scripts.

It does not authorize real media, scanner execution, ffmpeg processing, audio extraction, sync, transcription, subtitles, timeline export, SaaS/DB behavior, installer behavior, client-facing use, public demo, sales demo, or production use.

## Source Phase

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.QA.GATE.V1`

Current stable HEAD:

`2f215430daaaa8d3a7641f46cd94eb54da62f4ce`

## Input Contract

The visible report is derived only from already-safe controlled metadata JSON produced by the controlled-file metadata preflight contract.

The report input must require:

- `input_policy` equals `controlled_fixture_only`
- `input_path_redacted` is filename-only
- `ffprobe_command_kind` equals `metadata_json`
- `metadata.format` may be null or an object
- `metadata.streams` must be a list
- all safety flags remain false

If the preflight result is a failure, the visible report must still be safe and useful.

## Required Visible Report Sections

The report must include these human-readable sections:

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

## Forbidden Content

The visible report must not include:

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

## Failure Report Behavior

Failure reports must include:

- report title
- phase
- input policy
- redacted input filename when available
- preflight result
- safe failure reason when available
- empty or unavailable format summary
- zero-stream or unavailable stream summary
- blocked operations summary
- human review required note
- next safe phase

Failure reports must not expose full paths, private locations, raw scanner output, SaaS identifiers, DB identifiers, or runtime internals.

## Safety Boundary Summary

The safety boundary summary must state that this contract is local-only, controlled-fixture-only, and documentation/test-only.

It must state that human review is required before any later implementation phase.

## Blocked Operations Summary

The blocked operations summary must state that the visible report contract does not authorize:

- real rodaje material
- real media files
- scanner execution
- ffmpeg processing
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

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_PASS_READY_FOR_QA_GATE`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1`
