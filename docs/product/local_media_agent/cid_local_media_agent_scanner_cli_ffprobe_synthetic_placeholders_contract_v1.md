# CID Local Media Agent — Scanner CLI ffprobe Synthetic Placeholders Contract v1

## Phase

CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PLACEHOLDERS.CONTRACT.V1

## Objective

This phase defines the contract for future tiny synthetic placeholder files that may support ffprobe failure-path tests.

This phase is documentation-only and test-only.

It does not create placeholder files.

It does not create video files.

It does not create audio files.

It does not create binary fixtures.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not add subprocess runtime.

It does not modify scanner runtime.

It does not inspect real media.

## Current baseline

The project already has a declarative fixture_manifest.json under:

tests/fixtures/local_media_agent/ffprobe_synthetic/fixture_manifest.json

That manifest is manifest-only and does not authorize binary fixtures by itself.

This placeholders contract defines what a later explicit phase may create as tiny non-production placeholders.

## Future placeholder path

A later explicit phase may create placeholder files under:

tests/fixtures/local_media_agent/ffprobe_synthetic/

This contract phase must not create those files.

Only fixture_manifest.json may exist in that folder after this contract.

## Allowed future placeholder files

A later explicit implementation may create only these placeholder files:

- synthetic_unsupported_media_placeholder.txt
- synthetic_invalid_media_placeholder.bin
- synthetic_permission_denied_placeholder.dat

No other placeholder filename is allowed without another explicit phase.

## Placeholder purpose

The future placeholders are for failure-path tests only.

Allowed purposes:

- unsupported media status
- invalid or corrupt media status
- permission denied status

The placeholders must not be used to claim real technical probing, editorial intelligence, media sync, conform, delivery readiness or DaVinci/Avid/Premiere integration.

## Placeholder size policy

Future placeholders must remain tiny.

Limits:

- maximum text placeholder size: 4 KiB
- maximum invalid binary placeholder size: 4 KiB
- maximum permission placeholder size: 4 KiB
- maximum total placeholder size: 16 KiB

If larger files are needed, a separate phase must approve them.

## Placeholder content policy

Future placeholder content must be synthetic and harmless.

Allowed content:

- short ASCII text explaining it is synthetic
- deterministic tiny byte pattern for invalid binary placeholder
- empty or tiny file for permission scenario

Forbidden content:

- real video
- real audio
- real image
- real subtitle
- real transcript
- real camera original
- real sound roll
- real editorial export
- client material
- private pilot material
- downloaded stock media
- copyrighted media samples
- mobile phone clips
- drone clips
- screen recordings from real projects

## Privacy restrictions

Future placeholders must not contain:

- client names
- project names
- personal names
- production company names
- real location names
- real shoot dates
- GPS coordinates
- camera serial numbers
- lens serial numbers
- device serial numbers
- local user names
- home directory paths
- drive labels
- network paths
- cloud paths
- raw ffprobe output
- raw stdout
- raw stderr
- shell commands
- full argv

## Future manifest relationship

The future placeholder files must correspond to existing manifest entries.

Expected mapping:

- synthetic_unsupported_media_placeholder.txt -> synthetic_unsupported_media_placeholder
- synthetic_invalid_media_placeholder.bin -> synthetic_invalid_media_placeholder
- synthetic_permission_denied_placeholder.dat -> synthetic_permission_denied_placeholder

The manifest must remain relative-path only.

The manifest must not contain absolute paths.

The manifest must not authorize real media.

## Future test policy

A later placeholder implementation phase must test:

- placeholder file existence
- exact allowed filenames only
- size limits
- no real media extensions beyond the approved placeholder extensions
- no absolute path leaks
- no private metadata terms
- no source fixture modification
- no output beside source fixtures
- manifest alignment
- human review fields remain false until binary commit review is explicit

## Execution policy

Creating placeholders must not execute ffprobe.

Creating placeholders must not execute ffmpeg.

Creating placeholders must not add subprocess runtime.

The scanner must not read or process placeholders until a later explicit synthetic probe implementation phase.

## Human review

Human review is required before placeholder files become accepted test assets.

The reviewer must confirm:

- placeholders are synthetic
- placeholders are tiny
- placeholders contain no private metadata
- placeholders are not derived from real production material
- placeholders do not create product claims
- placeholders are safe to commit

## Real media remains blocked

Real media probing remains blocked after this contract.

A future real media phase must be explicit and separate.

## Non-goals

This phase does not implement placeholder creation.
This phase does not create .txt, .bin or .dat placeholder files.
This phase does not create media files.
This phase does not execute ffprobe.
This phase does not execute ffmpeg.
This phase does not add subprocess runtime.
This phase does not modify scripts/cid_media_agent_scan.py.
This phase does not create technical_metadata output.
This phase does not touch SaaS runtime.
This phase does not touch DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger.

## Acceptance criteria

This contract is accepted when tests verify:

- phase name is present
- documentation-only and test-only scope is explicit
- placeholder files are not created in this phase
- only fixture_manifest.json exists in the future fixture folder
- allowed future placeholder filenames are documented
- placeholder size policy is documented
- placeholder privacy restrictions are documented
- manifest relationship is documented
- ffprobe, ffmpeg, subprocess and runtime remain out of scope
- real media remains blocked
