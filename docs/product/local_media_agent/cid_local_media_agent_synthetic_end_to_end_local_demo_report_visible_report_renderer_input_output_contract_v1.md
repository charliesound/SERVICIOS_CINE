# CID Local Media Agent — Visible Report Renderer Input Output Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.V1`

## Objective

This phase defines the exact input/output contract for a future minimal visible report renderer.

This phase is documentation/test-only.

It does not implement a renderer.

It does not create renderer code, generator code, loader code, template engine code, runtime code, scanner changes, SaaS integration, HTML report, PDF report, DOCX report, XLSX report, CSV report, Markdown report artifact, rendered report, ffprobe execution, ffmpeg execution, media probing, media processing, subtitles, NLE export, installer behavior, licensing behavior, billing behavior, storage behavior, or real media processing.

## Upstream Baseline

Latest stable upstream commit:

`3b26916`

Latest stable upstream tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-renderer-implementation-readiness-gate-v1-20260618`

Upstream implementation readiness gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_implementation_readiness_gate_v1.md`

Upstream renderer QA gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_qa_gate_v1.md`

Upstream renderer contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md`

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

## Contract Decision

`INPUT_OUTPUT_CONTRACT_STATUS=READY_FOR_VALIDATION`

The first future renderer implementation should target a controlled Markdown report artifact.

Reason:

Markdown is the safest first visible artifact because it is local, plain text, diffable, reviewable, dependency-light, and easy to inspect before any HTML, PDF, DOCX, or XLSX format is considered.

This phase does not create that Markdown report artifact.

## Future Renderer Input Schema

The future renderer may accept only one validated synthetic input object with these top-level sections:

- report_identity
- demo_status
- disclaimer_block
- source_fixture_reference
- project_overview
- media_inventory_summary
- sync_readiness_summary
- transcription_subtitle_readiness_summary
- editorial_assistance_summary
- technical_risk_summary
- department_notes
- blocked_claims
- human_review_requirements
- limitations
- next_steps
- render_options

The input must be synthetic.

The input must be sanitized.

The input must be validated before rendering.

The input must not contain raw scanner dumps.

The input must not contain raw ffprobe dumps.

The input must not contain raw ffmpeg logs.

The input must not contain real source-media paths.

The input must not contain client identifiers.

The input must not contain secrets, credentials, tokens, or private machine data.

## Required Input Fields

The future renderer input must include:

- report_title
- report_language
- synthetic_demo_label
- local_first_privacy_notice
- no_real_media_processed_notice
- no_ffprobe_executed_notice
- no_ffmpeg_executed_notice
- no_real_sync_notice
- no_real_transcription_notice
- no_real_translation_notice
- no_real_nle_export_notice
- mandatory_human_review_notice
- assistive_not_substitutive_notice
- generated_from_synthetic_fixture_id
- fixture_version
- report_sections
- review_checklist

## Render Plan

The future renderer must render sections in this order:

1. title
2. synthetic demo disclaimer
3. executive summary
4. local-first privacy notice
5. project overview
6. media inventory summary
7. sync readiness summary
8. transcription and subtitle readiness summary
9. editorial assistance summary
10. technical risk summary
11. department notes
12. blocked claims
13. limitations
14. human review checklist
15. next steps

The renderer must not invent sections.

The renderer must not infer real technical results.

The renderer must not hide disclaimers.

The renderer must not reorder disclaimers below operational conclusions.

## Future Output Format

The first future output format is:

`markdown_visible_report_v1`

The future file extension is:

`.md`

The future artifact is a plain-text Markdown report for local review.

This phase does not create the file.

This phase does not create a renderer.

This phase does not create filesystem write behavior.

HTML, PDF, DOCX, XLSX, and CSV outputs remain future formats and are not authorized by this contract.

## Future Output Path Policy

A future renderer implementation may write only to an explicit controlled output directory.

The output directory must be provided by a safe caller or test harness.

The output path must be deterministic.

The output path must not target:

- source media folders
- private workspace folders
- user home root
- system directories
- repository root
- backend directories
- frontend directories
- database directories
- Alembic directories
- Docker directories
- fixture directories
- scanner source directories

The future implementation must use a safe temporary directory in automated tests.

The future implementation must not overwrite existing files unless a separate safe overwrite policy explicitly allows it.

## Future Artifact Naming Policy

The future Markdown artifact name must avoid real project identifiers.

Allowed future filename pattern:

`cid_local_media_agent_synthetic_visible_report_v1.md`

Not allowed:

- client names
- production names
- real project titles
- usernames
- machine names
- source folder names
- media filenames
- dates that imply real delivery
- final delivery labels

## Future Redaction Policy

The future renderer must redact or reject:

- absolute paths
- private source paths
- usernames
- machine names
- client identifiers
- production-sensitive identifiers
- media filenames if not synthetic
- credentials
- tokens
- secrets
- raw scanner dumps
- raw ffprobe dumps
- raw ffmpeg logs

## Future Safe Overwrite Policy

The default future behavior must be no overwrite.

If an output path already exists, the future renderer must fail safely unless an explicit safe overwrite option is provided.

The safe overwrite option must be false by default.

The safe overwrite option must be visible in the render options.

## Future Render Options

Allowed future render options:

- output_dir
- output_filename
- language
- include_department_notes
- include_human_review_checklist
- include_limitations
- safe_overwrite

Not allowed future render options:

- scan_source_media
- run_ffprobe
- run_ffmpeg
- call_saaS
- upload_media
- inspect_real_media
- generate_final_subtitles
- export_nle
- hide_disclaimers
- mark_as_final_delivery

## Claims Policy

The future output must not claim that CID has:

- analyzed real media
- synchronized real audio and video
- transcribed real dialogue
- translated real subtitles
- generated final subtitles
- exported to DaVinci Resolve
- exported to Avid
- exported to Premiere
- validated final delivery
- completed postproduction
- replaced a producer
- replaced a director
- replaced an editor
- replaced an assistant editor
- replaced a DIT
- replaced a sound team
- uploaded client media

## Human Review Policy

The future output must include a visible human review checklist.

The future output must state that the report is synthetic.

The future output must state that it is not a final technical diagnosis.

The future output must state that it is not a final postproduction report.

The future output must state that any real client use requires human verification.

## Blocked Scope

This phase does not create or modify:

- renderer code
- generator code
- loader code
- template engine code
- runtime code
- report artifact
- rendered report
- Markdown report artifact
- HTML report
- PDF report
- DOCX report
- XLSX report
- CSV report
- scanner runtime
- SaaS runtime
- backend
- frontend
- database
- Alembic migration
- Docker configuration
- storage integration
- billing integration
- licensing integration
- installer behavior
- ffprobe execution
- ffmpeg execution
- external binary execution
- media probing
- video analysis
- audio analysis
- waveform sync
- timecode sync
- clap sync
- transcription
- translation
- subtitle generation
- DaVinci Resolve export
- Avid export
- Premiere export
- OTIO export
- EDL export
- XML export
- FCPXML export
- client media
- real media
- private media
- source media

## Next Allowed Phase

The next allowed phase is:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.QA.GATE.V1`

That phase must remain documentation/test-only.

OpenCode should be used as read-only auditor before any implementation phase.

## Acceptance Criteria

This contract is valid only if:

- it declares the correct phase
- it references upstream commit `3b26916`
- it references the upstream readiness gate
- it references the renderer QA gate
- it references the renderer contract
- it references the synthetic fixture
- it chooses Markdown as the first future controlled output format
- it defines exact future input sections
- it defines required input fields
- it defines render order
- it defines output path policy
- it defines artifact naming policy
- it defines redaction policy
- it defines safe overwrite policy
- it defines allowed render options
- it defines blocked render options
- it preserves local-only behavior
- it preserves synthetic-only demonstration
- it preserves Spanish-first stakeholder readability
- it preserves mandatory human review
- it blocks unsafe real-capability claims
- it blocks artifact creation in this phase
- it blocks renderer implementation in this phase
- it blocks scanner changes
- it blocks SaaS integration
- it blocks ffprobe and ffmpeg execution
- it blocks real media processing

## QA Status

`RENDERER_INPUT_OUTPUT_CONTRACT_READY_FOR_VALIDATION`

Commit is blocked until target tests, related tests, staged scope safety check, fixture integrity check, WSL guard, and PostgreSQL-only regression guard pass.
