# CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Renderer Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.RENDERER.CONTRACT.V1`

## Objective

This phase defines the contract for a future minimal visible report renderer for the synthetic local demo report.

This phase is documentation/test-only.

It does not implement a renderer.

It does not create HTML, PDF, DOCX, XLSX, CSV, Markdown report artifact, rendered report, generator, loader, runtime, scanner change, SaaS integration, ffprobe execution, ffmpeg execution, media probing, media processing, subtitles, NLE export, installer behavior, licensing behavior, billing behavior, storage behavior, or real media processing.

## Upstream Baseline

Latest stable upstream commit:

`ee0d355`

Latest stable upstream tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-artifact-contract-qa-gate-v1-20260618`

Upstream artifact QA gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_qa_gate_v1.md`

Upstream artifact contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_v1.md`

Upstream mapping contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md`

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

## Future Renderer Definition

The future renderer will be responsible for transforming a validated synthetic report data structure into a stakeholder-readable visible report artifact.

The renderer must be deterministic.

The renderer must be local-only.

The renderer must be Spanish-first.

The renderer must preserve all visible disclaimers.

The renderer must preserve mandatory human review.

The renderer must present CID as assistive, not substitutive.

The renderer must not infer real technical results that are not present in the validated synthetic fixture or mapped report structure.

## Future Renderer Inputs

Future renderer inputs may include:

- validated synthetic report fixture
- validated mapping result
- visible report template structure
- report metadata
- demo disclaimer block
- human review checklist state
- safe rendering options

The future renderer must not read private source-media folders directly.

The future renderer must not scan disks.

The future renderer must not run ffprobe.

The future renderer must not run ffmpeg.

The future renderer must not inspect real media.

The future renderer must not call SaaS services by default.

The future renderer must not perform network calls by default.

## Future Renderer Outputs

Future renderer outputs may later include one or more controlled artifact formats:

- HTML report
- PDF report
- DOCX report
- Markdown report
- XLSX summary

This phase does not create any of those outputs.

This phase does not choose an implementation library.

This phase does not create rendering code.

This phase does not create a template engine.

This phase does not create filesystem write behavior.

## Renderer Safety Rules

Any future renderer must:

- render only sanitized fields
- preserve synthetic demo labeling
- preserve local-first privacy notice
- preserve no-real-media-processing disclaimer
- preserve no-sync-real disclaimer
- preserve no-transcription-real disclaimer
- preserve no-translation-real disclaimer
- preserve no-NLE-export-real disclaimer
- preserve mandatory human review block
- avoid raw scanner output
- avoid raw ffprobe output
- avoid raw ffmpeg logs
- avoid absolute paths
- avoid usernames
- avoid machine names
- avoid client identifiers
- avoid secrets
- avoid credentials
- avoid tokens

## Renderer Claims Policy

The future renderer must not state or imply that CID has:

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

## Stakeholder Readability

The future renderer must produce a visible report understandable to:

- producción
- productor
- montaje
- ayudante de montaje
- DIT
- sonido
- subtítulos
- dirección
- postproducción

The renderer must avoid overly technical raw dumps.

The renderer must separate executive summary, department notes, risks, limitations, and next steps.

## Future Implementation Gate

Before any renderer implementation, a separate implementation readiness gate must confirm:

- target format
- input schema
- output path policy
- redaction policy
- fixture integrity policy
- no real media policy
- no network default policy
- no ffprobe execution policy
- no ffmpeg execution policy
- no SaaS integration policy
- human review policy
- manual approval before creating any visible artifact

## Blocked Scope

This phase does not create or modify:

- renderer code
- generator code
- loader code
- template engine code
- report artifact
- rendered report
- HTML report
- PDF report
- DOCX report
- XLSX report
- CSV report
- Markdown report artifact
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

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1`

That phase must remain documentation/test-only.

OpenCode should be used as read-only auditor before any implementation readiness or renderer implementation phase.

## Acceptance Criteria

This contract is valid only if:

- it declares the correct phase
- it references upstream commit `ee0d355`
- it references the upstream artifact QA gate
- it references the artifact contract
- it references the mapping contract
- it references the synthetic fixture
- it defines a future renderer without implementing it
- it preserves local-only behavior
- it preserves Spanish-first stakeholder readability
- it preserves synthetic-only demonstration
- it preserves mandatory human review
- it preserves CID as assistive and not substitutive
- it blocks unsafe real-capability claims
- it blocks artifact creation in this phase
- it blocks renderer, generator, loader, and runtime implementation
- it blocks scanner changes
- it blocks SaaS integration
- it blocks ffprobe and ffmpeg execution
- it blocks real media processing
- it allows only a follow-up documentation/test-only QA gate

## QA Status

`RENDERER_CONTRACT_READY_FOR_VALIDATION`

Commit is blocked until target tests, related tests, staged scope safety check, fixture integrity check, WSL guard, and PostgreSQL-only regression guard pass.
