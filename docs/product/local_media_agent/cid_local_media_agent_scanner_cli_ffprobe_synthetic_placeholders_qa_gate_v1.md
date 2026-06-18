# CID Local Media Agent — Scanner CLI ffprobe Synthetic Placeholders QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PLACEHOLDERS.QA.GATE.V1`

## Objective

This phase audits the synthetic placeholder package created for future ffprobe failure-path work.

The gate verifies that the placeholder package is stable, local-only, non-audiovisual and safe to use as controlled test input in later phases.

## Scope

This phase is QA/test-only.

It validates:

- the existing synthetic placeholder files
- the existing fixture manifest
- the placeholder policy recorded in the manifest
- compatibility with previous synthetic fixture contracts
- absence of real media extensions in placeholder paths
- absence of private path leakage
- absence of runtime execution changes

## Files under QA

The expected fixture root is:

`tests/fixtures/local_media_agent/ffprobe_synthetic/`

Expected files:

- `fixture_manifest.json`
- `synthetic_invalid_media_placeholder.bin`
- `synthetic_permission_denied_placeholder.dat`
- `synthetic_unsupported_media_placeholder.txt`

Expected test file:

- `tests/unit/test_cid_local_media_agent_scanner_cli_ffprobe_synthetic_placeholders_create.py`

## Allowed placeholder extensions

Only these extensions are allowed for the current placeholders:

- `.bin`
- `.dat`
- `.txt`

## Forbidden placeholder extensions

The current placeholder package must not create or reference real audiovisual file extensions in placeholder paths.

Forbidden extensions include:

- `.mp4`
- `.mov`
- `.mxf`
- `.wav`
- `.aif`
- `.aiff`
- `.mp3`

These extensions may appear only as values inside policy fields that explicitly list forbidden extensions.

## Runtime restrictions

This QA gate does not execute ffprobe.

This QA gate does not execute ffmpeg.

This QA gate does not add subprocess runtime.

This QA gate does not inspect real media.

This QA gate does not modify scanner runtime.

This QA gate does not modify CID SaaS runtime.

## Privacy restrictions

The placeholder package must not include:

- private user paths
- Windows paths
- WSL mount paths
- environment files
- local database files
- real project media
- client media
- script content
- production content

## Required assertions

The QA gate must confirm:

1. The manifest is valid JSON.
2. The manifest declares `synthetic_placeholders_phase`.
3. The manifest tracks exactly 3 synthetic placeholders.
4. Each placeholder has `media_kind` equal to `not_media`.
5. Each placeholder has `must_not_be_valid_media` set to true.
6. Each placeholder has `must_not_execute_ffprobe` set to true.
7. Each placeholder has `must_not_execute_ffmpeg` set to true.
8. The fixture root contains exactly the manifest plus the 3 approved placeholders.
9. Each placeholder is smaller than 1024 bytes.
10. Each placeholder includes a synthetic marker.
11. No placeholder contains common media container markers.
12. No placeholder path uses real audiovisual extensions.
13. Previous fixture/manifest/contract tests remain compatible.
14. WSL and PostgreSQL-only guards remain clean.

## Pass criteria

This phase passes only if:

- all QA tests pass
- existing placeholder creation tests pass
- existing synthetic manifest tests pass
- existing synthetic contract tests pass
- `guard_wsl_repo.sh` passes
- the database-regression guard passes
- no runtime file is modified
- no media-processing executable is invoked

## Explicit non-goals

This phase does not:

- run ffprobe
- run ffmpeg
- parse media metadata
- create real video
- create real audio
- create DaVinci timelines
- add runtime execution code
- touch backend
- touch database
- touch Alembic
- touch Docker
- touch frontend
- touch Stripe
- touch workers
- touch CID SaaS runtime

## Result

This QA gate prepares the project for a later failure-path contract phase.

It does not authorize actual ffprobe execution yet.
