# CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Template Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.QA.GATE.V1`

## Objective

This phase validates the previously closed visible report template contract before any visible report artifact or renderer-related implementation is allowed.

The upstream contract under review is:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.V1`

Upstream document:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md`

Upstream test:

`tests/unit/test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract.py`

Upstream commit:

`ea0ea55`

Upstream tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-template-contract-v1-20260618`

This QA gate is documentation/test-only.

It does not create a visible report.

It does not create HTML, PDF, DOCX, XLSX, CSV, Markdown report artifacts, renderers, generators, fixture loaders, scanner runtime changes, SaaS integration, ffprobe execution, ffmpeg execution, external binary execution, installer behavior, licensing behavior, billing behavior, storage behavior, or any media processing.

## Gate Decision

`PASS_WITH_CONDITIONS_TO_VISIBLE_REPORT_TEMPLATE_FIXTURE_MAPPING_CONTRACT`

This means the visible report template contract is considered ready to be used as a controlled reference for the next documentation/test-only phase, provided all conditions in this QA gate remain true.

The next allowed phase is:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.V1`

That next phase may define how fields from the existing synthetic fixture JSON would map into the visible report template.

That next phase must not create a rendered report, report generator, HTML, PDF, DOCX, XLSX, Markdown report artifact, loader runtime, scanner runtime, ffprobe execution, ffmpeg execution, SaaS integration, installer behavior, licensing behavior, billing behavior, storage behavior, or real media processing.

## Allowed Scope

This QA gate may only add:

- this QA gate document
- one unit test file validating this QA gate document and the upstream template contract

Allowed files:

- `docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate.py`

## Blocked Scope

The following are explicitly blocked in this phase:

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
- scanner runtime change
- SaaS runtime change
- backend change
- frontend change
- database change
- Alembic migration
- Docker change
- storage change
- billing change
- installer change
- licensing change
- payment change
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
- client paths
- raw ffprobe output
- raw scanner output
- secrets
- credentials

## QA Inputs

The QA gate reviews the upstream template contract against these fixed product constraints:

1. The report is Spanish-first.
2. The report must be readable by production stakeholders.
3. The report must be understandable for productor, montaje, ayudante de montaje, DIT, sonido, subtítulos y producción.
4. The report must use synthetic data only.
5. The report must be local-first.
6. The report must not claim real analysis.
7. The report must not claim real synchronization.
8. The report must not claim real transcription.
9. The report must not claim real translation.
10. The report must not claim real export.
11. The report must keep human review mandatory.
12. The report must state that CID helps the team and does not replace creative, editorial, production, or technical judgment.

## Required Visible Disclaimers

Any future visible report based on the template must include visible disclaimers equivalent to the following meaning:

- Demo sintética.
- Datos ficticios.
- No se ha procesado material real.
- No se ha ejecutado ffprobe ni ffmpeg.
- No representa un análisis técnico final.
- No representa sincronización real.
- No representa transcripción real.
- No representa traducción real.
- No representa exportación real a NLE.
- Revisión humana obligatoria.
- CID ayuda al equipo, no sustituye el criterio creativo, técnico ni de producción.

These disclaimers must be visible to a non-technical stakeholder.

They must not be hidden only in metadata, comments, tests, source code, logs, or internal documentation.

## Required Template Areas

The upstream template contract is considered acceptable only if it defines or protects these visible areas:

- report title area
- executive summary area
- local-first privacy notice area
- synthetic dataset notice area
- project overview area
- media inventory summary area
- sync readiness summary area
- transcription/subtitle readiness summary area
- editorial assistance summary area
- technical risk summary area
- department-facing notes area
- blocked claims area
- human review area
- next steps area
- limitations area

The template may later evolve, but it must preserve the difference between:

- synthetic demonstration
- real technical analysis
- final editorial decision
- final production decision

## Data Binding QA Rules

The upstream contract must separate template structure from fixture values.

The template must not hard-code real media names, client names, project names, personal names, filesystem paths, source-media paths, secrets, credentials, or production-sensitive details.

Future mapping may reference the existing synthetic fixture JSON, but this QA gate does not create that mapping.

Existing synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

This phase does not modify that fixture.

## Claim Safety Rules

The template must not make or enable these claims:

- CID has analyzed real media.
- CID has synchronized real audio and video.
- CID has transcribed real dialogue.
- CID has translated real subtitles.
- CID has generated final subtitles.
- CID has exported to DaVinci Resolve.
- CID has exported to Avid.
- CID has exported to Premiere.
- CID has produced final editorial decisions.
- CID has replaced a DIT, assistant editor, sound team, editor, producer, or director.
- CID has processed client footage.
- CID has uploaded client footage.
- CID has validated final delivery.
- CID has completed conform, color, sound post, VFX, or mastering.

## Local-First Privacy QA Rules

The template must preserve these local-first rules:

- source media remains on the client's controlled machine
- no upload by default
- no SaaS dependency for local operation
- only authorized metadata or reports may be shared in future phases
- no raw client media paths in stakeholder reports
- no raw technical dumps in stakeholder reports
- no private source media names in stakeholder reports by default

## Human Review QA Rules

The template must keep human review as a visible operational requirement.

The future report may assist decisions, but it must not close decisions.

Human review remains mandatory for:

- synchronization quality
- transcription quality
- subtitle quality
- editorial use
- delivery decisions
- production decisions
- client-facing interpretation
- publication

## Gate Acceptance Criteria

This QA gate passes only if:

- the upstream template contract exists
- the upstream template contract declares its phase identifier
- the upstream template contract remains documentation/test-only
- this QA gate declares the upstream commit and tag
- this QA gate blocks artifact creation
- this QA gate blocks runtime implementation
- this QA gate blocks media processing
- this QA gate blocks ffprobe and ffmpeg execution
- this QA gate blocks SaaS integration
- this QA gate preserves Spanish-first stakeholder readability
- this QA gate preserves local-first privacy
- this QA gate preserves synthetic-only demonstration
- this QA gate preserves mandatory human review
- this QA gate blocks unsafe claims
- this QA gate allows only the next documentation/test-only mapping contract

## Explicit Non-Goals

This phase does not:

- implement report rendering
- implement template loading
- implement fixture loading
- implement fixture-to-template mapping
- implement report generation
- create a report artifact
- create a stakeholder PDF
- create a stakeholder HTML file
- create a stakeholder DOCX file
- create a stakeholder XLSX file
- create a stakeholder Markdown file
- modify scanner code
- modify ffprobe code
- execute ffprobe
- execute ffmpeg
- inspect media files
- process media files
- create subtitles
- translate subtitles
- export to an NLE
- integrate with DaVinci Resolve
- integrate with Avid
- integrate with Premiere
- integrate with CID SaaS
- touch billing
- touch licensing
- touch installers

## QA Status

`QA_GATE_READY_FOR_VALIDATION`

The phase can be committed only after:

- staged diff check passes
- target test passes
- related tests pass
- staged scope safety check passes
- WSL guard passes
- PostgreSQL-only regression guard passes
