# CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1`

## Objective

This phase defines the first stakeholder-readable visible report contract for the CID Local Media Agent standalone product demo line.

The purpose is to specify what a future synthetic visible report must contain, how it must be presented, and which claims remain blocked.

This phase is documentation/test-only.

It does not create a report file.

It does not create a report generator.

It does not create a report renderer.

It does not create a fixture loader.

It does not create runtime code.

It does not modify the scanner.

It does not modify SaaS code.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not process real media.

It does not create installer or licensing behavior.

## Baseline

Current stable HEAD before this phase:

`683785d`

Previous QA gate:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1`

Previous QA gate result:

`PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_VALIDATED_FOR_VISIBLE_REPORT_CONTRACT`

Validated fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

Standalone product blueprint:

`CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1`

## Report status

The future visible report must be presented as:

`SYNTHETIC_VISIBLE_DEMO_REPORT_CONTRACT_ONLY`

The future report must say clearly:

- synthetic demo data
- local-first product direction
- no real media analysis
- no client media processed
- no cloud upload
- no external binary execution
- no synchronization completed
- no transcription completed
- no subtitle translation completed
- no DaVinci export completed
- human review required before public-facing use

## Target audience

The visible report must be readable by:

- producers
- post supervisors
- editors
- assistant editors
- DITs
- sound teams
- subtitle/localization teams
- film school stakeholders
- trusted early contacts

The report must avoid deep engineering language in the main body.

Technical detail may appear only in an appendix or validation block.

## Required report sections

A future report that follows this contract must contain these sections in this order:

1. `Cover / Demo identity`
2. `Executive summary`
3. `Local-first privacy statement`
4. `Synthetic project inventory summary`
5. `Department review overview`
6. `Sync candidate overview`
7. `Warnings and human review queue`
8. `Suggested folder organization`
9. `What this demo proves`
10. `What this demo does not prove yet`
11. `Next product steps`
12. `Appendix: synthetic fixture validation`

## Section 1 — Cover / Demo identity

The cover must include:

- product name: `CID Local Media Agent`
- ecosystem name: `CID — Cinematic Intelligence Direction`
- report type: `Synthetic End-to-End Local Demo Report`
- fixture id: `SYNTHETIC_LOCAL_DEMO_001`
- fixture version: `v1`
- privacy level: `synthetic_safe_labels_only`
- status label: `synthetic demo, not real media analysis`

The cover must not include:

- client name
- project title
- production title
- real path
- raw filename
- real person name
- real location

## Section 2 — Executive summary

The executive summary must explain in plain language that the report shows how CID Local Media Agent can organize a local project inventory and prepare review work for postproduction teams.

It must include these synthetic counts from the fixture:

- 10 synthetic items
- 4 video-like items
- 3 audio-like items
- 1 still-image-like item
- 1 document-like item
- 1 ignored/unsupported item
- 6 sync candidate groups
- 10 items requiring human review

The summary must make clear that these are demo values from a synthetic fixture.

## Section 3 — Local-first privacy statement

The report must state that CID Local Media Agent is designed as a local-first standalone product.

The privacy statement must include:

- customer media stays local by default
- video and audio are not uploaded by default
- cloud upload is false in the synthetic fixture
- external binary execution is false in the synthetic fixture
- the fixture uses synthetic safe labels only
- no private paths are present
- no raw filenames are present
- no client names are present
- no person names are present
- no real locations are present
- no script content is present
- no dialogue content is present
- no transcription content is present

## Section 4 — Synthetic project inventory summary

The report must show the inventory summary as a readable table or grouped list.

Minimum visible columns:

- safe item label
- category
- duration hint
- technical hint
- sync group
- review status
- department review

The report must not expose raw filenames.

The report must not expose local paths.

The report must not expose real camera card names.

The report must not expose real recorder card names.

## Section 5 — Department review overview

The report must summarize review needs for:

- editorial review
- assistant editor review
- DIT review
- sound review
- subtitle review
- production review
- ignore/archive review

The report must use production language, not engineering-only language.

Examples of acceptable wording:

- `Needs assistant editor review`
- `Needs DIT review`
- `Needs sound review`
- `Ready for subtitle review`
- `Review before ingest`
- `Archive or ignore candidate`

Examples of blocked wording:

- `Automatically synchronized`
- `Automatically transcribed`
- `Automatically translated`
- `Ready for final delivery`
- `Validated for broadcast`
- `Budget-safe`
- `Legally cleared`

## Section 6 — Sync candidate overview

The report must show sync groups as candidates only.

Allowed wording:

- `Candidate sync group`
- `Possible double-system sound`
- `Needs human sync review`
- `Timecode appears unavailable in synthetic metadata`
- `Frame-rate mismatch warning`
- `Sample-rate mismatch warning`

Blocked wording:

- `Synced`
- `Matched`
- `Locked`
- `Conformed`
- `Ready for edit without review`
- `Waveform sync complete`
- `Timecode sync complete`
- `Clap sync complete`

## Section 7 — Warnings and human review queue

The report must include a warning queue.

Required warning coverage:

- `MISSING_TIMECODE`
- `POSSIBLE_DOUBLE_SYSTEM_SOUND`
- `FRAME_RATE_MISMATCH`
- `SAMPLE_RATE_MISMATCH`
- `NEEDS_HUMAN_REVIEW`
- `READY_FOR_EDITOR_REVIEW`
- `READY_FOR_DIT_REVIEW`
- `READY_FOR_SOUND_REVIEW`
- `READY_FOR_SUBTITLE_REVIEW`
- `UNSUPPORTED_CONTAINER_HINT`

The report must group warnings by practical production impact.

Recommended grouping:

- editorial organization
- DIT/media management
- sound/sync review
- subtitle/localization review
- unsupported/archive review

## Section 8 — Suggested folder organization

The report must show the suggested folders:

- `01_VIDEO`
- `02_AUDIO`
- `03_STILLS`
- `04_DOCUMENTS`
- `05_REPORTS`
- `06_REVIEW_NEEDED`
- `07_EXPORTS_FOR_EDIT`

The report must clarify that this folder structure is a suggested organization plan, not an executed file operation.

The report must not claim files were moved.

The report must not claim files were copied.

The report must not claim files were renamed.

## Section 9 — What this demo proves

The report may claim:

- the product direction is understandable
- synthetic inventory can be structured safely
- review queues can be explained to postproduction roles
- department-oriented reporting can be designed
- local-first privacy language can be preserved
- a future visible report can be generated from safe synthetic data after implementation

The report must frame these as demo-readiness claims, not runtime capability claims.

## Section 10 — What this demo does not prove yet

The report must state that the demo does not yet prove:

- real media scanning
- real metadata extraction
- ffprobe integration
- ffmpeg integration
- waveform synchronization
- timecode synchronization
- clap synchronization
- transcription
- speaker detection
- language detection
- subtitle translation
- DaVinci export
- Avid export
- Premiere export
- installer behavior
- license activation
- customer deployment
- SaaS synchronization

## Section 11 — Next product steps

The report may list next steps:

1. visible report QA gate
2. synthetic report template contract
3. synthetic report renderer contract
4. local fixture loader contract
5. visible report generator implementation gate
6. local-only demo packaging plan
7. human review before external presentation

These are planning steps only.

## Section 12 — Appendix: synthetic fixture validation

The appendix must include:

- fixture path
- schema version
- fixture id
- item count
- category distribution
- warning coverage
- department review coverage
- privacy assertions
- validation rules
- known limitations

The appendix must be clearly separated from the producer-facing summary.

## Visual and language rules

The report must be readable in Spanish first.

English labels may remain for technical fixture identifiers.

The report must use clear section headers.

The report must favor production language:

- montaje
- ayudante de montaje
- DIT
- sonido
- subtítulos
- revisión humana
- organización de material
- cola de revisión
- candidatos de sincronía
- privacidad local

The report must avoid exaggerated claims.

The report must avoid SaaS claims.

The report must avoid AI replacement claims.

The report must present CID as assisted workflow, not creative replacement.

## Required visible disclaimers

The report must include:

- `Datos sintéticos de demostración`
- `No se ha analizado material real`
- `No se ha subido vídeo ni audio`
- `No se ha ejecutado ffprobe ni ffmpeg`
- `No se ha sincronizado material real`
- `No se ha transcrito material real`
- `No se ha traducido subtítulos reales`
- `Revisión humana obligatoria`
- `No usar como informe técnico final`

## Blocked public claims

The report must not claim:

- real footage has been scanned
- real sound has been synchronized
- real clips have been transcribed
- real subtitles have been translated
- real media has been organized on disk
- export to DaVinci is complete
- export to Avid is complete
- export to Premiere is complete
- the tool is production-certified
- the tool is legally certified
- the tool is ready for unattended customer deployment
- the tool replaces the editor
- the tool replaces the assistant editor
- the tool replaces the DIT
- the tool replaces the sound team
- the tool replaces human review

## Safe commercial framing

Safe framing:

`CID Local Media Agent muestra, con datos sintéticos, cómo podría organizarse un proyecto local para revisión de montaje, DIT, sonido y subtítulos sin subir vídeo ni audio.`

Safe framing:

`Este reporte no demuestra todavía análisis real de material, pero sí fija una estructura comprensible para enseñar el valor del producto a contactos de confianza.`

Safe framing:

`La herramienta está orientada a asistir al equipo, no a sustituir el criterio del montador, DIT, sonidista o productor.`

## Contract decision

Contract decision:

`SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_QA`

This decision allows only the next documentation/test-only QA gate.

It keeps renderer implementation blocked.

It keeps generator implementation blocked.

It keeps loader implementation blocked.

It keeps scanner runtime changes blocked.

It keeps SaaS integration blocked.

It keeps external binary execution blocked.

It keeps real media processing blocked.

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1`
