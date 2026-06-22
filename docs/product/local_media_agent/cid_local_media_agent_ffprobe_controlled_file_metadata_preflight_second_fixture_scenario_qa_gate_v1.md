# CID Local Media Agent - FFprobe Controlled File Metadata Preflight Second Fixture Scenario QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.QA.GATE.V1`

## Objective

Validate the second controlled fixture scenario for the ffprobe controlled-file metadata preflight.

This QA gate confirms that the second fixture scenario validates a more realistic mocked metadata result while preserving the existing runtime boundaries.

## Source Stable State

HEAD:

`d0d9b44d2c8c6dfd6d9f1267f12593e1ad382637`

Commit:

`test: add CID Local Media Agent ffprobe second fixture scenario`

Tag:

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-preflight-second-fixture-scenario-v1-20260620`

## Source Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.V1`

## Required Source Files

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_second_fixture_scenario_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_second_fixture_scenario.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight.py`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_qa_gate.py`

## Required Validated Behavior

The second fixture scenario must validate:

- controlled fixture path only
- mocked successful ffprobe metadata response
- preservation of `metadata.format`
- preservation of `metadata.streams`
- at least one video stream in mocked metadata
- at least one audio stream in mocked metadata
- `ffprobe_command_kind` equals `metadata_json`
- `input_path_redacted` is filename only
- full input path is not leaked
- uncontrolled paths remain rejected
- missing `--controlled-fixture` remains rejected
- all blocked execution flags remain false
- no forbidden imports
- no ffmpeg execution/reference
- runtime script remains unchanged

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

- real rodaje material
- real media files
- arbitrary folders
- scanner execution
- ffmpeg media processing
- audio extraction
- sync generation
- transcription generation
- subtitle generation
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

- second fixture scenario QA gate test passing
- second fixture scenario test passing
- ffprobe controlled metadata preflight test passing
- ffprobe controlled metadata preflight QA gate test passing
- ffmpeg availability preflight QA gate test passing
- py_compile passing
- required source files present
- source stable state declared
- required acceptance result declared
- next safe phase declared
- forbidden import check passing
- no ffmpeg execution/reference check passing
- runtime script not staged
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing
- no protected files staged

## QA Gate Decision

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_VALIDATED`

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_QA_GATE_PASS_CLOSED`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.V1`
