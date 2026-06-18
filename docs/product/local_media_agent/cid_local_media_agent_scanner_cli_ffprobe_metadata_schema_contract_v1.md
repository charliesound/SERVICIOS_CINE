# CID Local Media Agent — Scanner CLI ffprobe Metadata Schema Contract v1

## Phase

CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.METADATA.SCHEMA.CONTRACT.V1

## Objective

This phase defines the allowed future technical metadata schema for local ffprobe media probing before any future phase executes ffprobe against media files.

This phase is contract-only and test-only.

## Current status

The scanner currently supports an optional --ffprobe-preflight availability check.

That preflight may check whether ffprobe exists locally, but it must not probe media files yet.

This schema contract does not change runtime behavior.

## Non-goals

This phase does not implement media probing.
This phase does not execute ffprobe against video files.
This phase does not execute ffprobe against audio files.
This phase does not call ffmpeg.
This phase does not parse real technical metadata.
This phase does not create proxies.
This phase does not transcribe media.
This phase does not create subtitles.
This phase does not create DaVinci files.
This phase does not touch SaaS runtime.
This phase does not touch DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger.

## Metadata container

Future technical metadata must be stored under the existing asset-level field technical_metadata.

The field must remain an object.

Before real probing, the current safe value may remain an empty object.

This is not a runtime implementation in this phase.

## Allowed top-level fields

Future technical metadata may persist only these top-level fields:

- probe_status
- probe_warning_code
- duration_seconds
- format_name
- stream_count
- video
- audio

## Allowed video fields

- codec_name
- codec_type
- width
- height
- frame_rate
- timecode_detected

## Allowed audio fields

- codec_name
- codec_type
- sample_rate
- channel_count

## Probe status values

- not_requested
- skipped
- available
- missing
- timeout
- invalid_json
- permission_denied
- unsupported_media
- probe_failed
- privacy_redacted

## Probe warning codes

- ffprobe_missing
- ffprobe_timeout
- ffprobe_invalid_json
- ffprobe_permission_denied
- ffprobe_unsupported_media
- ffprobe_probe_failed
- ffprobe_privacy_redacted
- ffprobe_metadata_incomplete

## Forbidden persisted data

The scanner must not persist these values by default:

- full raw ffprobe JSON
- raw stdout
- raw stderr
- absolute input paths
- absolute output paths
- executable path to ffprobe
- local user names
- home directory paths
- environment variables
- shell command strings
- original command argv
- complete stream tags
- complete format tags
- device names
- volume names
- network paths
- cloud URLs

## Raw ffprobe output

Raw ffprobe output must not be stored by default.

A future debug mode may be considered only if explicit debug opt-in is provided, output remains local-only, unsafe diagnostics are marked as unsafe for sharing, absolute paths are redacted, executable paths are redacted and human review is required before external sharing.

## Path-policy integration

The metadata schema must not bypass scanner path-policy.

Default scanner outputs must still avoid local absolute paths.

Path exposure must continue to be controlled by:

- sanitized_path
- local_relative_path
- hashed_path
- redacted_path
- local_absolute_path

local_absolute_path must remain explicit opt-in only.

## Output integration

Future metadata may be included in:

- 01_media_catalog/media_catalog.json
- 01_media_catalog/technical_metadata.json
- 01_media_catalog/media_catalog.csv
- 01_media_catalog/media_catalog.md
- 00_project/processing_status.json

The scanner must not create outputs outside --output-root.

## Human review

Technical metadata is production assistance, not final truth.

Human review is required before using metadata for editorial decisions, sync decisions, timecode decisions, conform decisions, delivery assumptions, DaVinci handoff, Avid handoff, Premiere handoff or external production reports.

## Future implementation gate

A future implementation phase may execute ffprobe on synthetic placeholder fixtures only after this schema contract is accepted.

Real media probing must remain blocked until a later explicit phase.

The first future implementation must use synthetic fixtures only, use bounded subprocess execution, use timeout, use explicit argv list, avoid shell=True, avoid raw output persistence, preserve local-only behavior, preserve path-policy behavior and keep SaaS and database out of scope.
