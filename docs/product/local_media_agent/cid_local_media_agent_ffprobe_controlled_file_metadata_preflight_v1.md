# CID Local Media Agent — FFprobe Controlled File Metadata Preflight v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1`

## Objective

This phase authorizes only controlled-file `ffprobe` metadata preflight for explicitly controlled fixture paths.

It is local-only.

It is not client-facing.

It is not installer readiness.

## Controlled Inputs

The preflight may accept only paths under:

- `/tmp/cid_local_media_agent_controlled_ffprobe/`
- `tests/fixtures/local_media_agent/controlled_media/`

The CLI requires all of these flags:

```bash
python scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py --input <path> --json --controlled-fixture
```

Unexpected positional arguments are rejected.

Paths outside the controlled roots are rejected.

Full input paths are not included in JSON output; only the file name is reported.

## Allowed Command

The only allowed command shape is:

```bash
ffprobe -v error -print_format json -show_format -show_streams <input>
```

## Blocked Scope

This phase does not authorize:

- real media use
- real media probing
- real media processing
- scanner execution
- `ffmpeg` usage
- audio extraction
- synchronization
- transcription
- subtitle creation
- timeline export
- SaaS upload
- database write
- network call
- installer behavior
- client-facing use

## Output Contract

Returned JSON includes:

- `phase`
- `result`
- `input_policy: controlled_fixture_only`
- `input_path_redacted`
- `ffprobe_command_kind: metadata_json`
- `metadata.format`
- `metadata.streams`
- `media_processing_performed: false`
- `scanner_executed: false`
- `real_media_used: false`
- `ffmpeg_used: false`
- `audio_extraction_performed: false`
- `sync_generated: false`
- `transcription_generated: false`
- `subtitles_generated: false`
- `timeline_export_generated: false`
- `database_write: false`
- `saas_upload: false`
- `network_call: false`

If `ffprobe` fails, the result is `FFPROBE_METADATA_PREFLIGHT_FAILED` and all safety flags remain false.

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_PASS_READY_FOR_QA_GATE`
