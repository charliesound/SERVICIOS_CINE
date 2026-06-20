# CID Local Media Agent - Visible Report Alignment v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.ALIGNMENT.V1`

## Objective

Define the internal demo visible report expected from the current scanner baseline outputs.

This phase is docs/test-only.

This phase does not execute the scanner.

This phase does not modify runtime code.

This phase does not create a real report file yet.

## Source Phase

Source alignment phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.POST.EXECUTION.ALIGNMENT.V1`

Source result:

`LOCAL_MEDIA_AGENT_POST_EXECUTION_ALIGNMENT_PASS_CURRENT_SCANNER_BASELINE_ACCEPTED_WITH_ROADMAP_OUTPUT_DELTAS`

Source stable HEAD:

`b7465b28d6450f1f736e4a41f0ebf7b485adea03`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-scenario-post-execution-alignment-v1-20260620`

## Current Accepted Scanner Baseline

The visible report must be based only on the accepted current scanner output families:

- `00_project/`
- `01_media_catalog/`
- `99_logs/`

The report must not claim that the current baseline already performs:

- audio sync
- transcription
- subtitle generation
- translation
- reports beyond the current scanner artifacts
- DaVinci Resolve export
- Avid export
- client-facing delivery

## Intended Audience

The report is intended for internal technical demo review by production, post-production, and product stakeholders.

The report must be readable by a producer without requiring direct inspection of JSON files.

The report must be clear enough to explain what the local scanner already does and what remains roadmap.

## Required Visible Sections

The future visible report should contain these sections:

1. Executive summary
2. Local-only privacy confirmation
3. Input fixture summary
4. Media candidate summary
5. Accepted media by extension
6. Rejected non-media by extension
7. Human review required items
8. Warning path summary
9. Created output files summary
10. Roadmap outputs not yet generated
11. Producer interpretation
12. Next recommended technical actions

## Required Data Points

The visible report must expose these data points when available from current scanner outputs or stdout evidence:

- `status = completed_with_warnings`
- `privacy_mode = local_only`
- `candidate_media_count = 5`
- `human_review_required_count = 1`
- `warnings_count = 1` if available from stdout or derived from warning list length
- warning message `unknown synthetic placeholder`
- accepted extension counts `.mov=1`, `.mp4=2`, `.wav=1`
- rejected extension counts `.exe=1`, `.txt=2`
- ffprobe preflight `skipped`
- privacy event `local_only_scan_completed`
- privacy event `original_media_left_client_system = false`

## Producer Interpretation Rules

The visible report must explain the result in production language:

- The scanner found valid media candidates.
- The scanner rejected non-media files instead of treating them as assets.
- The scanner raised a human review warning for ambiguous material.
- The scanner remained local-only.
- The scanner did not run sync, transcription, subtitles, or export modules.
- The warning-path exit code is expected for this controlled demo.

## Roadmap Disclosure Rules

The visible report must explicitly label the following as roadmap or future modules:

- `02_audio_sync/`
- `03_transcription/`
- `04_subtitles/`
- `05_reports/`
- `06_exports/`

The visible report must not present those directories as already implemented runtime outputs.

## Privacy Rules

The visible report must not leak local user names, machine names, Windows paths, WSL paths outside approved synthetic demo context, repo paths, or real client material.

Forbidden tokens include:

- `/mnt/`
- Windows drive paths
- UNC paths
- `DESKTOP-`
- `harliesound`
- `SERVICIOS_CINE`

The report may refer to the synthetic demo root only when explicitly marked as approved synthetic demo context.

## Non-Goals

This phase does not authorize:

- runtime report generation
- scanner code changes
- real media scanning
- public demo use
- client-facing demo use
- ffprobe execution
- ffmpeg execution
- audio synchronization
- transcription
- subtitle generation
- translation
- DaVinci Resolve export
- SaaS upload
- database writes
- network calls
- frontend/backend SaaS changes
- Docker or Alembic changes
- Stripe, AI Jobs, credits, or ledger changes

## Alignment Decision

The current scanner baseline is ready to be represented by a visible internal demo report.

The visible report should clarify that the scanner baseline is real and local-only, while sync, transcription, subtitles, reports, and exports remain roadmap modules.

## Result

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_ALIGNMENT_PASS_READY_FOR_VISIBLE_REPORT_CONTRACT`

## Next Recommended Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTRACT.V1`
