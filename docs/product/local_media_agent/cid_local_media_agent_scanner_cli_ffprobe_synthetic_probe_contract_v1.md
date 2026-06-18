# CID Local Media Agent — Scanner CLI ffprobe Synthetic Probe Contract v1

## Phase

CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PROBE.CONTRACT.V1

## Objective

This phase defines the future contract for the first controlled ffprobe probing step using synthetic placeholder fixtures only.

This phase is contract-only and test-only.

It does not execute ffprobe.

It does not modify scanner runtime.

It does not parse media metadata.

It does not inspect real video or audio files.

## Current baseline

The scanner currently supports safe local scanning, strict local-only privacy behavior, path-policy controls, optional --ffprobe-preflight availability check and an ffprobe metadata schema contract.

The scanner must not probe media files in this phase.

## Scope

This contract defines how a later implementation phase may test ffprobe probing safely with synthetic fixtures.

The future synthetic probe phase may only use controlled fixture files created for tests.

It must not use production footage, real client material, camera originals, sound rolls, proxies, subtitles from real projects or private documents.

## Non-goals

This phase does not implement ffprobe probing.
This phase does not execute ffprobe.
This phase does not execute ffmpeg.
This phase does not add subprocess runtime.
This phase does not read real media metadata.
This phase does not create technical_metadata output.
This phase does not create proxies.
This phase does not transcribe media.
This phase does not create subtitles.
This phase does not create DaVinci outputs.
This phase does not touch SaaS runtime.
This phase does not touch DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger.

## Future synthetic fixture rule

A later implementation may use synthetic fixture assets only.

Allowed fixture characteristics:

- generated for tests
- tiny duration
- no client content
- no production content
- no personal names
- no project names
- no real locations
- no embedded private metadata
- safe to commit if explicitly approved
- documented as synthetic

Forbidden fixture characteristics:

- real camera originals
- real sound files
- real editorial exports
- real client proxies
- real subtitle files from projects
- real screenshots
- real thumbnails
- real transcripts
- private production documents

## Future command execution requirements

The future implementation must use safe bounded execution.

Required controls:

- explicit argv list
- no shell=True
- timeout
- captured stdout
- captured stderr
- stderr truncation
- no command template expansion
- no environment secret exposure
- no executable path exposure in persisted output
- no raw stdout persistence by default
- no raw stderr persistence by default

## Future allowed probing mode

The first future implementation may only probe synthetic fixture paths produced or controlled by the test suite.

The scanner must reject or skip real media probing unless a later explicit phase authorizes it.

The future implementation must include a test-only gate or fixture-only guard.

## Future output restrictions

The future synthetic probe may write only local outputs under --output-root.

Allowed future output files:

- 01_media_catalog/media_catalog.json
- 01_media_catalog/technical_metadata.json
- 00_project/processing_status.json
- 99_logs/warnings.json
- 99_logs/errors.json
- 99_logs/privacy_events.json

The scanner must not create outputs outside --output-root.

## Future metadata restrictions

Future synthetic probing must respect the previously approved metadata schema.

Allowed metadata fields remain limited to:

- probe_status
- probe_warning_code
- duration_seconds
- format_name
- stream_count
- video
- audio
- codec_name
- codec_type
- width
- height
- frame_rate
- timecode_detected
- sample_rate
- channel_count

The scanner must not persist full raw ffprobe JSON.

The scanner must not persist full stream tags or full format tags.

## Privacy requirements

Future synthetic probe outputs must not expose absolute input paths, absolute output paths, ffprobe executable path, local user names, home directory paths, environment variables, shell commands, raw argv, raw stdout, raw stderr, device names, volume names, network paths or cloud URLs.

The existing path-policy remains authoritative.

local_absolute_path must remain explicit opt-in only.

## Failure handling

Future synthetic probing must use controlled statuses and warnings.

Required future failure statuses:

- skipped
- missing
- timeout
- invalid_json
- permission_denied
- unsupported_media
- probe_failed
- privacy_redacted

Required future warning codes:

- ffprobe_missing
- ffprobe_timeout
- ffprobe_invalid_json
- ffprobe_permission_denied
- ffprobe_unsupported_media
- ffprobe_probe_failed
- ffprobe_privacy_redacted
- ffprobe_metadata_incomplete

Failures must not expose tracebacks to normal CLI users.

Failures must not dump raw ffprobe diagnostics by default.

## Human review

Even synthetic technical metadata must be treated as assistance, not truth.

Human review is required before using future ffprobe metadata for editorial decisions, sync decisions, timecode decisions, conform decisions, delivery assumptions, DaVinci handoff, Avid handoff, Premiere handoff or external production reports.

## Real media remains blocked

Real media probing remains blocked after this contract.

A future real media phase must be explicit and separate.

That future phase must first prove synthetic probing is safe, bounded, privacy-preserving and test-covered.

## Acceptance criteria

This contract is accepted when tests verify contract-only scope, no runtime scanner probing added, no subprocess runtime added in this phase, synthetic fixtures only, real media remains blocked, safe subprocess requirements, output restrictions, metadata restrictions, privacy restrictions, human review requirements and SaaS/database out of scope.
