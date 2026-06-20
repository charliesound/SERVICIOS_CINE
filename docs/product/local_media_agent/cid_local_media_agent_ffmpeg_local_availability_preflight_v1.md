# CID Local Media Agent — FFmpeg Local Availability Preflight v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.V1`

## Objective

This phase adds a small local-only preflight that checks whether `ffmpeg` and `ffprobe` are available on the current machine.

The preflight only detects local tool availability.

It is not a media scanner.

It is not installer readiness.

It is not client-facing.

## Allowed Behavior

The preflight may call only:

- `ffmpeg -version`
- `ffprobe -version`

The preflight uses `shutil.which` to locate binaries and `subprocess.run` only for the version commands above.

## Blocked Scope

This phase does not authorize:

- media processing
- media probing
- scanner execution
- ffprobe or ffmpeg calls with media input files
- real media folder scans
- client media inspection
- network calls
- SaaS uploads
- database writes
- installer behavior
- frontend changes
- backend runtime changes
- Docker changes
- Alembic changes

## Output Contract

The script returns JSON with these fields:

- `phase`
- `result`
- `ffmpeg.available`
- `ffmpeg.path`
- `ffmpeg.version_line`
- `ffprobe.available`
- `ffprobe.path`
- `ffprobe.version_line`
- `media_processing_performed: false`
- `scanner_executed: false`
- `real_media_used: false`
- `database_write: false`
- `saas_upload: false`
- `network_call: false`

If either binary is missing or cannot answer the version command, the script still emits JSON and marks that tool unavailable.

## CLI

```bash
python scripts/local_media_agent/ffmpeg_local_availability_preflight.py --json
```

The CLI does not accept media path arguments.

## Safety Position

No media is processed.

No scanner is executed.

No ffprobe or ffmpeg media probing is authorized.

No real media is used.

Human review remains required before any future operational use.

CID remains assistive, not substitutive.

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFMPEG_LOCAL_AVAILABILITY_PREFLIGHT_PASS_READY_FOR_QA_GATE`
