# CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Template Fixture Mapping Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.V1`

## Objective

This phase defines the documentation/test-only mapping contract between the existing synthetic demo fixture and the previously validated visible report template.

The purpose is to specify how synthetic fixture fields may be bound to stakeholder-readable report sections in a future phase, without creating a rendered report, report artifact, loader, renderer, generator, runtime, scanner change, ffprobe execution, ffmpeg execution, SaaS integration, installer behavior, licensing behavior, billing behavior, storage behavior, or real media processing.

This phase is documentation/test-only.

It defines a fixture-to-template mapping contract.

It does not execute the mapping.

It does not load the fixture at runtime.

It does not render any visible report.

## Upstream Inputs

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

Visible report template contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md`

Visible report template QA gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate_v1.md`

Latest upstream stable commit:

`1c5b441`

Latest upstream stable tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-template-contract-qa-gate-v1-20260618`

## Gate Decision

`MAPPING_CONTRACT_READY_FOR_VALIDATION`

This contract may be used only after validation by its unit test, related tests, staged scope safety check, WSL guard, and PostgreSQL-only regression guard.

The next allowed phase after this one is:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.QA.GATE.V1`

That next phase must remain documentation/test-only.

## Fixture Discovery Snapshot

The fixture root shape observed during contract creation is:

`object`

Top-level fixture keys or root description:

- `client_material_used` — `boolean`
- `cloud_upload` — `boolean`
- `created_for_ecosystem` — `string`
- `created_for_product` — `string`
- `external_binary_execution` — `boolean`
- `fixture_id` — `string`
- `fixture_kind` — `string`
- `fixture_version` — `string`
- `human_review_required` — `boolean`
- `items` — `array`
- `limitations` — `array`
- `local_input_label` — `string`
- `local_output_label` — `string`
- `next_recommended_phase` — `string`
- `privacy_assertions` — `object`
- `privacy_level` — `string`
- `project_summary` — `object`
- `schema_version` — `string`
- `source_mode` — `string`
- `suggested_folders` — `array`
- `validation_rules` — `object`

This snapshot records only fixture structure.

It does not copy real media values, client values, private paths, credentials, secrets, or source-media identifiers.

The fixture is synthetic and must remain synthetic.

## Mapping Principles

The mapping contract follows these rules:

1. Template areas must be fed only by synthetic fixture data.
2. Report sections must preserve Spanish-first stakeholder readability.
3. Data bindings must be descriptive and reviewable by humans.
4. Missing fixture fields must degrade to visible placeholder copy, not hidden failure.
5. Null or empty values must be shown as pending, unavailable, not applicable, or requiring human review.
6. No synthetic value may be presented as a real technical result.
7. No mapped value may claim real analysis, real synchronization, real transcription, real translation, or real NLE export.
8. Raw technical dumps must not be exposed in the stakeholder report.
9. Client paths, source-media paths, private names, secrets, and credentials must be excluded.
10. Human review remains mandatory for every operational interpretation.

## Mapping Table

| Mapping ID | Template Area | Fixture Source Policy | Display Rule | Human Review Rule |
|---|---|---|---|---|
| `VRM-001` | report title area | bind from synthetic project identity fields if present | show synthetic demo title and product name | reviewer confirms it is visibly marked as demo |
| `VRM-002` | executive summary area | bind from synthetic summary and readiness fields if present | show concise producer-readable summary | reviewer confirms no final technical claim |
| `VRM-003` | local-first privacy notice area | bind from fixed local-first policy copy, not fixture values | show that media remains local by default | reviewer confirms no upload-by-default claim |
| `VRM-004` | synthetic dataset notice area | bind from fixed synthetic disclaimer copy | show demo sintética and datos ficticios | reviewer confirms disclaimer is visible |
| `VRM-005` | project overview area | bind from synthetic project metadata if present | show safe synthetic project overview | reviewer confirms no real client/project value |
| `VRM-006` | media inventory summary area | bind from synthetic inventory counts or grouped media summary if present | show high-level counts and categories only | reviewer confirms no raw source path is shown |
| `VRM-007` | sync readiness summary area | bind from synthetic sync readiness fields if present | show readiness as simulated/planned, not completed | reviewer confirms no real sync claim |
| `VRM-008` | transcription and subtitle readiness area | bind from synthetic language/subtitle readiness fields if present | show possible workflow status as synthetic | reviewer confirms no real transcription claim |
| `VRM-009` | editorial assistance summary area | bind from synthetic editorial assistance notes if present | show assistant-editor-oriented notes | reviewer confirms no final edit decision |
| `VRM-010` | technical risk summary area | bind from synthetic risk fields if present | show risk labels and review notes | reviewer confirms risks are non-final |
| `VRM-011` | department-facing notes area | bind from synthetic department notes if present | group notes for producción, montaje, DIT, sonido, subtítulos | reviewer confirms departments can understand the report |
| `VRM-012` | blocked claims area | bind from fixed blocked-claims copy | show what the demo has not done | reviewer confirms no unsafe claim appears elsewhere |
| `VRM-013` | human review area | bind from fixed human-review requirement copy | show required review checklist | reviewer confirms review is mandatory |
| `VRM-014` | next steps area | bind from synthetic next-step recommendations if present | show controlled next actions only | reviewer confirms no runtime work is implied |
| `VRM-015` | limitations area | bind from fixed limitations copy and synthetic caveats if present | show limitations prominently | reviewer confirms limitations are visible |

## Selector Policy

This phase does not define executable selectors.

Future selector syntax may be defined later, but this phase uses non-runtime descriptive bindings only.

Allowed selector descriptions:

- `synthetic project identity fields if present`
- `synthetic summary and readiness fields if present`
- `synthetic project metadata if present`
- `synthetic inventory counts or grouped media summary if present`
- `synthetic sync readiness fields if present`
- `synthetic language/subtitle readiness fields if present`
- `synthetic editorial assistance notes if present`
- `synthetic risk fields if present`
- `synthetic department notes if present`
- `synthetic next-step recommendations if present`
- `fixed local-first policy copy`
- `fixed synthetic disclaimer copy`
- `fixed blocked-claims copy`
- `fixed human-review requirement copy`
- `fixed limitations copy`

Blocked selector behavior:

- executable query language
- runtime fixture loading
- filesystem traversal
- media probing
- external binary execution
- environment-variable access
- network access
- database access
- SaaS access
- secret lookup
- client path exposure
- raw source-media path exposure

## Missing Data Policy

If a future report section cannot find a mapped synthetic field, it must show stakeholder-readable fallback copy.

Allowed fallback wording examples:

- `Pendiente de completar en datos sintéticos`
- `No disponible en esta demo sintética`
- `No aplicable a este ejemplo sintético`
- `Requiere revisión humana`
- `No representa un análisis técnico real`

Fallback copy must not hide missing data.

Fallback copy must not imply that CID performed real processing.

## Redaction Policy

The future mapping must exclude:

- client media names
- private source-media names
- private source-media paths
- absolute local filesystem paths
- usernames
- machine names
- credentials
- tokens
- secrets
- raw scanner dumps
- raw ffprobe dumps
- raw ffmpeg logs
- production-sensitive identifiers
- private project identifiers
- unapproved client identifiers

The stakeholder report must remain safe for a producer-facing demo.

## Claims Policy

The future mapped report must not claim that CID has:

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

## Spanish-First Stakeholder Language

The future visible report must be written first in Spanish.

The language must be understandable to:

- productor
- producción
- montaje
- ayudante de montaje
- DIT
- sonido
- subtítulos
- dirección
- postproducción

The report may later support English, but this mapping contract validates the Spanish-first path only.

## Human Review Policy

Human review is mandatory before any stakeholder-facing interpretation.

Human review must cover:

- whether the demo is clearly synthetic
- whether disclaimers are visible
- whether mapped fields are understandable
- whether no unsafe capability claim appears
- whether no private path or private identifier appears
- whether the report helps production and postproduction teams
- whether CID is presented as assistive, not substitutive

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

## Acceptance Criteria

This contract is valid only if:

- the existing synthetic fixture exists
- the visible report template contract exists
- the visible report template QA gate exists
- the mapping contract declares the correct phase
- the mapping contract references the fixture path
- the mapping contract records fixture structure without copying values
- the mapping contract defines at least 15 mapping IDs
- the mapping contract preserves Spanish-first stakeholder readability
- the mapping contract preserves local-first privacy
- the mapping contract preserves synthetic-only demonstration
- the mapping contract preserves mandatory human review
- the mapping contract blocks unsafe real-capability claims
- the mapping contract blocks rendering and runtime implementation
- the mapping contract does not modify the fixture
- the mapping contract allows only a follow-up documentation/test-only QA gate

## QA Status

`MAPPING_CONTRACT_READY_FOR_VALIDATION`

This phase can be committed only after:

- staged diff check passes
- target test passes
- related tests pass
- staged scope safety check passes
- WSL guard passes
- PostgreSQL-only regression guard passes
