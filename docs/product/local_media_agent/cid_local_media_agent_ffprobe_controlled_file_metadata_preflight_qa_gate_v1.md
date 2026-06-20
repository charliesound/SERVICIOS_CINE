# CID Local Media Agent - FFprobe Controlled File Metadata Preflight QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.QA.GATE.V1`

## Objective

Validate the controlled-file ffprobe metadata preflight.

This QA gate validates that ffprobe metadata probing is available only for explicitly controlled fixture files and that all output remains safe, redacted, local-only, and non-destructive.

## Source Stable State

HEAD:

`5c8d1d96c128bf3b8457dac71e55b83d18759ca8`

Commit:

`feat: add CID Local Media Agent ffprobe controlled metadata preflight`

Tag:

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-preflight-v1-20260620`

## Source Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1`

## Required Source Files

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_v1.md`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight.py`

## Required Validated Behavior

The source phase must:

- require `--input`
- require `--json`
- require `--controlled-fixture`
- reject uncontrolled paths
- reject missing controlled fixture authorization
- reject unexpected positional arguments
- use ffprobe only for metadata JSON
- never call ffmpeg
- never scan real folders
- never process real media
- redact full input paths from JSON output
- preserve safe failure behavior
- preserve all blocked execution flags as false

## Required Safe JSON Fields

The CLI JSON must include:

- `phase`
- `result`
- `input_policy`
- `input_path_redacted`
- `ffprobe_command_kind`
- `metadata.format`
- `metadata.streams`
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

## Required Safe Flags

The following flags must remain false:

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

## Required Boundaries

This QA gate does not authorize:

- real media or rodaje material
- arbitrary folders
- scanner execution
- ffmpeg media processing
- audio extraction
- sync
- transcription
- subtitles
- timeline export
- SaaS upload
- database writes
- installer creation
- client-facing use
- public demo
- sales demo
- production use

## Validation Evidence Required

This QA gate is accepted only with:

- QA gate test passing
- source phase test passing
- FFmpeg availability preflight QA gate test passing
- py_compile passing
- controlled empty fixture JSON smoke test passing
- uncontrolled path rejection passing
- missing controlled fixture flag rejection passing
- full path redaction passing
- forbidden import check passing
- no ffmpeg execution pattern passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing
- no protected files staged

## QA Gate Decision

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_VALIDATED`

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_QA_GATE_PASS_CLOSED`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.V1`
