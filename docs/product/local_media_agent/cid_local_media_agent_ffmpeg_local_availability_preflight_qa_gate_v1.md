# CID Local Media Agent - FFmpeg Local Availability Preflight QA Gate v1

## Phase

CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.QA.GATE.V1

## Objective

Validate the FFmpeg and ffprobe local availability preflight.

This QA gate validates only tool availability detection and safe JSON reporting.

It does not authorize media processing.
It does not authorize scanner execution.
It does not authorize ffmpeg execution on media files.
It does not authorize ffprobe execution on media files.
It does not authorize real media folders.
It does not authorize sync.
It does not authorize transcription.
It does not authorize subtitles.
It does not authorize timeline export.
It does not authorize SaaS upload.
It does not authorize database writes.
It does not authorize installer creation.
It does not authorize client-facing use.

## Source Stable State

HEAD:

4d6410ae72d37598834acae1adc0249526eb8362

Commit:

feat: add CID Local Media Agent FFmpeg availability preflight

Tag:

cid-dev-stable-local-media-agent-ffmpeg-local-availability-preflight-v1-20260620

## Source Phase

CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.V1

## Required Source Files

- docs/product/local_media_agent/cid_local_media_agent_ffmpeg_local_availability_preflight_v1.md
- scripts/local_media_agent/ffmpeg_local_availability_preflight.py
- tests/unit/test_cid_local_media_agent_ffmpeg_local_availability_preflight.py

## Required Behavior

The preflight must:

- detect ffmpeg availability
- detect ffprobe availability
- report ffmpeg path
- report ffprobe path
- report ffmpeg version line
- report ffprobe version line
- emit valid JSON through the CLI
- accept no media path argument
- continue safely when a tool is missing
- continue safely when version lookup fails
- keep all blocked execution flags false

## Required Safe Flags

The CLI JSON must preserve:

- media_processing_performed: false
- scanner_executed: false
- real_media_used: false
- database_write: false
- saas_upload: false
- network_call: false

## Required Rejections

The CLI must reject unexpected positional arguments such as media paths.

This prevents accidental use of the availability preflight as a media processing command.

## Required Boundaries

The QA gate confirms:

- no real media processing
- no scanner execution
- no media probing
- no media conversion
- no audio extraction
- no sync generation
- no transcription generation
- no subtitle generation
- no timeline export
- no SaaS upload
- no database writes
- no installer creation
- no client-facing claim
- no public demo claim
- no sales demo claim

## Validation Evidence Required

This QA gate is accepted only with:

- FFmpeg local availability preflight QA gate test passing
- FFmpeg local availability preflight test passing
- py_compile passing
- CLI JSON smoke test passing
- safe flags check passing
- unexpected media argument rejection passing
- forbidden import check passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing
- no protected files staged

## QA Gate Decision

PASS_FFMPEG_LOCAL_AVAILABILITY_PREFLIGHT_VALIDATED

This closes only the availability preflight QA gate.

It does not open real media processing.
It does not open ffprobe media probing.
It does not open ffmpeg media processing.
It does not open audio extraction.
It does not open sync.
It does not open transcription.
It does not open subtitles.
It does not open timeline export.
It does not open SaaS integration.
It does not open database writes.
It does not open installer creation.

## Acceptance Result

LOCAL_MEDIA_AGENT_FFMPEG_LOCAL_AVAILABILITY_PREFLIGHT_QA_GATE_PASS_CLOSED

## Next Safe Phase

CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1
