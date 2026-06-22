# CID Local Media Agent — FFprobe Controlled File Metadata Preflight Second Fixture Scenario v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.V1`

## Objective

This phase defines a second controlled fixture scenario for the existing `ffprobe` controlled-file metadata preflight.

It is documentation/test-only around a mocked fixture scenario.

It does not change runtime behavior.

It does not modify the existing preflight script.

## Upstream

Source-controlled preflight phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.QA.GATE.V1`

Current stable HEAD:

`982e788294da527854005f52e5674a7ec5ef73a1`

Existing source files:

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_v1.md`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight.py`
- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_qa_gate.py`

## Scenario Scope

This is only a second controlled fixture scenario.

The scenario validates a mocked successful `ffprobe` JSON response containing:

- `format.filename`
- `format.duration`
- `format.size`
- `format.format_name`
- at least one video stream with codec, width, height, and duration metadata
- at least one audio stream with codec, sample rate, channels, and duration metadata

The scenario must use only controlled fixture paths.

The scenario must use mocked `subprocess.run`.

The scenario must not require real media files.

## Blocked Scope

This phase does not authorize:

- real media
- rodaje material
- arbitrary folders
- folder scanning
- scanner execution
- `ffmpeg` media processing
- audio extraction
- sync
- transcription
- subtitles
- timeline export
- SaaS upload
- database write
- installer behavior
- client-facing use
- public demo
- sales demo
- production use

## Safety Assertions

The second scenario must confirm:

- `metadata.format` is preserved
- `metadata.streams` is preserved
- full input paths are not leaked
- `input_path_redacted` is filename-only
- `ffprobe_command_kind` remains `metadata_json`
- all blocked operation flags remain `false`
- uncontrolled paths remain rejected
- missing `--controlled-fixture` remains rejected
- forbidden imports are absent
- no `ffmpeg` execution pattern is present

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_PASS_READY_FOR_QA_GATE`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.QA.GATE.V1`
