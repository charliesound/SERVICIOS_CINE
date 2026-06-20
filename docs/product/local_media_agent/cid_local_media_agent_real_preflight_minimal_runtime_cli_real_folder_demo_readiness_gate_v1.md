# CID Local Media Agent — Real Folder Demo Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.READINESS.GATE.V1`

## Objective

Validate that the current CID Local Media Agent scanner baseline is ready to prepare a controlled local demo scenario.

This readiness gate is not the demo itself.

This readiness gate does not execute the scanner.

This readiness gate does not create demo media.

This readiness gate does not use real client material.

This readiness gate is docs/test-only.

## Required prior QA gate

This phase depends on:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.BOUNDED.IMPLEMENTATION.QA.GATE.V1`

Required prior result:

`PRODUCT_SEMANTICS_BOUNDED_IMPLEMENTATION_QA_GATE_PASS`

## Demo readiness result

`LOCAL_MEDIA_AGENT_DEMO_READINESS_GATE_PASS_CONTROLLED_LOCAL_SYNTHETIC_ONLY`

## Current demo-ready capabilities

The current scanner baseline is ready to support a controlled local demo showing:

- local-only folder scan
- sanitized local path policy
- scanner-safe output folders
- JSON summary output
- processing status output
- media catalog output
- accepted media extension counts
- rejected non-media extension counts
- ignored extension counts remaining empty
- `.mov` and `.wav` accepted as media in the controlled scenario
- `.txt` and `.exe` rejected as non-media in the controlled scenario
- rejected non-media files excluded from the media catalog
- legacy `UNKNOWN` synthetic placeholder `.txt` still requiring human review

## Demo material boundary

The next demo phase may use only:

- synthetic placeholder files
- local temporary folders
- sanitized folder names
- fake project names
- fake clip names
- fake media placeholders created for testing

The next demo phase must not use:

- real client material
- real shoot material
- private production names
- private locations
- private people names
- real scripts
- real audio
- real video
- real subtitles
- real transcripts

## Demo execution boundary

This readiness gate does not authorize demo execution.

A later demo scenario phase must separately authorize any local scanner execution.

The later demo scenario must remain local-only and must not use cloud, SaaS calls, uploads, network calls, database writes, media probing, media decoding, transcription, translation, subtitles, sync, or NLE export.

## Product claim boundary

This readiness gate does not authorize:

- client-facing clean classification PASS claims
- production-ready claims
- commercial release claims
- public demo claims
- sales deck claims
- product launch claims

The demo may only be described as:

`controlled local technical demo preparation`

## Allowed later demo scenario

Recommended next phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTRACT.V1`

That later phase should define:

- exact synthetic folder shape
- exact allowed placeholder file names
- exact command shape
- expected sanitized output
- expected JSON summary fields
- expected output folders
- expected privacy checks
- expected no-goals
- abort conditions
- validation chain

## Runtime boundary

This readiness gate changes no runtime files.

No scanner behavior is changed by this readiness gate.

No report behavior is changed by this readiness gate.

No CLI behavior is changed by this readiness gate.

## Protected scope still blocked

This readiness gate does not authorize:

- SaaS backend changes
- SaaS frontend changes
- database changes
- Docker changes
- Alembic changes
- Stripe changes
- AI Jobs changes
- credits changes
- ledger changes
- frontend changes
- backend changes
- media-processing implementation
- ffmpeg execution
- ffprobe execution beyond existing availability preflight
- transcription
- translation
- subtitles
- sync
- NLE export
- report-expansion scope

## Validation evidence required before closing this gate

This gate must validate:

- demo readiness gate test passes
- bounded implementation QA gate passes
- bounded implementation tests pass
- scanner safe baseline passes
- scanner execution hardening passes
- scanner CLI contract passes
- WSL guard passes
- SQLite regression guard passes
- `git diff --check` passes

## Gate result

`PASS`

The repository is ready to prepare a controlled local synthetic demo scenario.

The repository is not yet authorized for public/client-facing demo claims.

The repository is not yet authorized to run a real client-material demo.
