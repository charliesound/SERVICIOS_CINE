# CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Artifact Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.ARTIFACT.CONTRACT.V1`

## Objective

This phase defines the future visible report artifact contract for the synthetic local demo report.

This phase is documentation/test-only.

It does not create any visible report artifact.

It does not create HTML, PDF, DOCX, XLSX, CSV, Markdown report artifact, renderer, generator, loader, runtime, scanner change, SaaS integration, ffprobe execution, ffmpeg execution, media probing, media processing, subtitles, NLE export, installer behavior, licensing behavior, billing behavior, storage behavior, or real media processing.

## Upstream Baseline

Latest stable upstream commit:

`897f067`

Latest stable upstream tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-template-fixture-mapping-contract-qa-gate-v1-20260618`

Upstream mapping QA gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_qa_gate_v1.md`

Upstream mapping contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md`

Upstream template contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md`

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

## Artifact Definition

The future visible report artifact is a stakeholder-readable synthetic demo report.

It is intended to show how CID Local Media Agent may present local media organization, sync readiness, transcription/subtitle readiness, editorial assistance notes, technical risks, department notes, limitations, and next steps.

The artifact must be Spanish-first.

The artifact must be understandable to:

- producción
- productor
- montaje
- ayudante de montaje
- DIT
- sonido
- subtítulos
- dirección
- postproducción

The artifact must be explicitly marked as synthetic.

The artifact must not be presented as a real technical analysis.

## Future Artifact Formats

Future phases may define one or more of these visible formats:

- HTML report
- PDF report
- DOCX report
- Markdown report
- XLSX summary

This phase does not create any of those formats.

This phase does not choose a renderer.

This phase does not choose a generator.

This phase does not create templates for real rendering.

## Required Visible Disclaimers

Any future artifact must visibly state:

- Demo sintética
- Datos ficticios
- No se ha procesado material real
- No se ha ejecutado ffprobe ni ffmpeg
- No representa un análisis técnico final
- No representa sincronización real
- No representa transcripción real
- No representa traducción real
- No representa exportación real a NLE
- Revisión humana obligatoria
- CID ayuda al equipo, no sustituye criterio creativo, técnico, editorial ni de producción

## Artifact Sections

The future artifact must include these sections:

- title
- executive summary
- local-first privacy notice
- synthetic dataset notice
- project overview
- media inventory summary
- sync readiness summary
- transcription and subtitle readiness summary
- editorial assistance summary
- technical risk summary
- department-facing notes
- blocked claims
- human review requirements
- next steps
- limitations

## Artifact Safety Rules

The future artifact must not expose:

- private source-media paths
- absolute filesystem paths
- usernames
- machine names
- private client identifiers
- production-sensitive identifiers
- credentials
- tokens
- secrets
- raw scanner dumps
- raw ffprobe dumps
- raw ffmpeg logs
- real media names by default
- private project names by default

## Claims Policy

The future artifact must not claim that CID has:

- analyzed real media
- synchronized real audio and video
- transcribed real dialogue
- translated real subtitles
- generated final subtitles
- exported to DaVinci Resolve
- exported to Avid
- exported to Premiere
- created a final edit decision
- replaced a DIT
- replaced an assistant editor
- replaced a sound team
- replaced an editor
- replaced a producer
- replaced a director
- uploaded client media
- validated final delivery
- completed postproduction

## Human Review Policy

Human review is mandatory before any stakeholder-facing interpretation.

Human review must cover:

- demo status
- disclaimers visibility
- mapped data meaning
- privacy and redaction safety
- sync-readiness interpretation
- transcription-readiness interpretation
- subtitle-readiness interpretation
- editorial interpretation
- department-facing interpretation
- limitations and next steps

## Blocked Scope

This phase does not create or modify:

- visible report artifact
- rendered report
- HTML report
- PDF report
- DOCX report
- XLSX report
- CSV report
- Markdown report artifact
- report renderer
- report generator
- fixture loader
- template engine runtime
- scanner runtime
- SaaS runtime
- backend
- frontend
- database
- Alembic migration
- Docker configuration
- storage integration
- billing integration
- installer behavior
- licensing behavior
- payment behavior
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

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.ARTIFACT.CONTRACT.QA.GATE.V1`

That phase must remain documentation/test-only.

## Acceptance Criteria

This contract is valid only if:

- it declares the correct phase
- it references upstream commit `897f067`
- it references the upstream tag
- it references the mapping QA gate
- it references the mapping contract
- it references the template contract
- it references the synthetic fixture
- it defines the future artifact without creating it
- it preserves Spanish-first stakeholder readability
- it preserves local-first privacy
- it preserves synthetic-only demonstration
- it preserves mandatory human review
- it blocks unsafe real-capability claims
- it blocks artifact creation in this phase
- it blocks runtime implementation
- it blocks scanner changes
- it blocks SaaS integration
- it blocks ffprobe and ffmpeg execution
- it blocks real media processing
- it allows only a follow-up documentation/test-only QA gate

## QA Status

`ARTIFACT_CONTRACT_READY_FOR_VALIDATION`

Commit is blocked until target tests, related tests, staged scope safety check, fixture integrity check, WSL guard, and PostgreSQL-only regression guard pass.

## Explicit Artifact Creation Block

This phase does not create any visible report artifact.
