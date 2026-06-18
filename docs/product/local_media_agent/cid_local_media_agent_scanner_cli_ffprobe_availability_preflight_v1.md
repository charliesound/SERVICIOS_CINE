# CID Local Media Agent — Scanner CLI ffprobe Availability Preflight v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.AVAILABILITY.PREFLIGHT.V1`

## Objective

This phase adds an optional local `ffprobe` availability preflight to the scanner CLI.

The scanner may now check whether `ffprobe` is available on the client machine, but it must not run `ffprobe` against media files yet.

This is the first controlled runtime step after the ffprobe contract phase.

## Scope

This phase may:

- add an explicit `--ffprobe-preflight` flag
- check local `ffprobe` availability
- return a controlled availability status
- warn with `ffprobe_missing` when unavailable
- keep the safe baseline scanner working when `ffprobe` is missing
- keep all outputs local
- add tests and this phase document

## Runtime rule

The availability preflight may only check whether the executable exists locally.

It must not:

- run `ffprobe` on video files
- run `ffprobe` on audio files
- parse real technical metadata
- persist codec metadata
- persist duration metadata
- persist stream metadata
- store raw `ffprobe` stdout
- store raw `ffprobe` stderr

## Privacy rule

The preflight must not expose:

- input absolute paths
- output absolute paths
- media file paths
- detected executable path
- environment variables
- shell commands
- raw diagnostics intended only for developers

The scanner must continue to use the existing path-policy for media catalog output.

## Missing ffprobe behavior

If `ffprobe` is not available and `--ffprobe-preflight` is requested, the scanner must:

- complete the safe baseline scan when normal scanner preflight passes
- return a controlled warning code: `ffprobe_missing`
- avoid traceback output
- avoid suggesting cloud upload
- avoid changing media catalog technical metadata
- avoid creating files outside `--output-root`

## Available ffprobe behavior

If `ffprobe` is available and `--ffprobe-preflight` is requested, the scanner may return:

- `requested=true`
- `status=available`
- `available=true`
- `warning_code=null`

It must not return the local executable path.

## Default behavior

If `--ffprobe-preflight` is not requested, the scanner must keep default behavior:

- no ffprobe availability check required
- no ffprobe warning
- no technical metadata extraction
- no media probing

## Non-goals

This phase does not implement media probing.

This phase does not call `ffprobe` on any media file.

This phase does not call `ffmpeg`.

This phase does not transcribe media.

This phase does not create subtitles.

This phase does not create proxies.

This phase does not create DaVinci outputs.

This phase does not touch SaaS runtime.

This phase does not touch DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger.

## Acceptance criteria

This phase is accepted when:

- the scanner exposes an explicit `--ffprobe-preflight` flag
- missing `ffprobe` produces a controlled `ffprobe_missing` warning
- available `ffprobe` produces an availability status without exposing executable paths
- default scanner behavior still works without requiring `ffprobe`
- no real media technical metadata is extracted
- no raw `ffprobe` stdout or stderr is persisted
- existing privacy/path-policy behavior remains intact
- existing safe baseline and execution hardening tests still pass
