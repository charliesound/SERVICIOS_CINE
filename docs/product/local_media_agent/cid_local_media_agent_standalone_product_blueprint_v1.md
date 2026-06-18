# CID Local Media Agent — Standalone Product Blueprint v1

## Phase

`CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1`

## Objective

This blueprint defines CID Local Media Agent as a complete standalone product inside the CID ecosystem.

CID Local Media Agent must be installable, usable, demoable, licensable, supportable, and commercially understandable as an individual product.

It may connect to CID SaaS in the future if the customer explicitly authorizes that connection, but it must not depend on CID SaaS to work.

This phase is documentation/test-only.

It does not implement application runtime.

It does not implement scanner runtime.

It does not implement SaaS integration.

It does not implement installer logic.

It does not implement licensing or activation logic.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not process client media.

It does not upload video files.

It does not upload audio files.

It does not create payment flows.

## Current baseline

Current stable HEAD before this blueprint:

`38fde44`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.V1`

Current product decision:

`CID_LOCAL_MEDIA_AGENT_IS_A_STANDALONE_PRODUCT_INSIDE_CID`

## Product identity

Product name:

`CID Local Media Agent`

Parent ecosystem:

`CID — Cinematic Intelligence Direction`

Product type:

`local-first audiovisual media analysis and postproduction preparation tool`

Commercial position:

`standalone CID product`

The product must be able to exist as an individual product even when the customer does not use CID SaaS.

## Relationship with CID SaaS

CID Local Media Agent and CID SaaS must be related but not dependent.

CID SaaS is the future central production platform.

CID Local Media Agent is a local tool installed on the customer's machine.

The correct relationship is:

- CID Local Media Agent works locally by default
- CID Local Media Agent can produce local reports
- CID Local Media Agent can be licensed as an individual product
- CID Local Media Agent may later send authorized metadata or reports to CID SaaS
- CID Local Media Agent must never require CID SaaS to scan local material
- CID Local Media Agent must never upload raw client video by default
- CID Local Media Agent must never upload raw client audio by default
- CID Local Media Agent must never expose private local paths without redaction
- CID Local Media Agent must allow offline work under controlled license rules

## Product promise

The product promise is:

"CID Local Media Agent analiza carpetas locales de material audiovisual sin subir vídeos ni audios a la nube, genera una radiografía técnica y editorial del material y ayuda a preparar montaje, sonido, subtítulos, revisión humana y postproducción."

This promise must remain realistic.

The product supports human creative and technical decisions.

It does not replace the editor, assistant editor, DIT, sound team, subtitle team, post supervisor, director, or producer.

## Target users

Primary users:

- editor
- assistant editor
- DIT
- postproduction supervisor
- sound editor
- documentary editor
- production company
- film school
- audiovisual training center

Secondary users:

- producer
- director
- assistant director
- archive coordinator
- subtitle coordinator
- distribution preparation team
- small production office

## Core use cases

The standalone product should support these future use cases:

1. Scan a local audiovisual folder.
2. Detect media-like files and production documents.
3. Build a safe inventory.
4. Extract or simulate technical metadata depending on authorization and stage.
5. Identify warnings and review needs.
6. Group likely camera and sound candidates.
7. Prepare editor-friendly reports.
8. Prepare sound-friendly reports.
9. Prepare subtitle and transcription readiness notes.
10. Prepare future DaVinci Resolve export readiness.
11. Keep all media local.
12. Export local JSON, Markdown, and HTML reports.
13. Optionally synchronize approved metadata with CID SaaS in a future phase.

## Product tiers

The product may later support commercial tiers.

### Demo tier

Purpose:

- show product value
- use synthetic or controlled sample data
- avoid client media
- show local reports
- avoid network dependency

### Individual professional tier

Purpose:

- editor or assistant editor working locally
- local folder analysis
- technical reports
- project organization suggestions
- limited activation count

### Studio or production company tier

Purpose:

- multiple seats
- shared license administration
- larger project folders
- team-oriented reports
- support and onboarding

### Education tier

Purpose:

- film schools
- training centers
- classroom demos
- controlled datasets
- reduced price or institutional licensing

## Platform support

The product should target:

- Windows
- macOS
- Linux

The future packaging strategy must define:

- installer or package per platform
- dependency checks
- ffmpeg and ffprobe strategy
- local model strategy for transcription when applicable
- update strategy
- rollback strategy
- support diagnostics
- code signing or notarization where required

This blueprint does not implement those installers.

## Local-first architecture

The product must be designed around a local-first architecture:

- local project input
- local processing
- local reports
- local logs
- local configuration
- local cache when needed
- redacted support bundle when authorized
- optional future CID SaaS connection

Network access must be optional for product operation, except for license activation, update checks, or customer-authorized CID synchronization.

## Privacy requirements

CID Local Media Agent must preserve strict privacy defaults:

- no video upload by default
- no audio upload by default
- no raw file upload by default
- no private path upload by default
- no client title upload by default
- no script content upload by default
- no dialogue upload by default
- no transcription upload by default
- no automatic cloud analysis by default
- no telemetry containing client media identifiers
- safe labels and redaction by default
- customer authorization required before any sync

## Future CID SaaS connection principles

A future CID SaaS connection may support:

- license status
- organization seats
- update entitlement
- anonymized feature usage counters
- customer-approved report upload
- customer-approved metadata upload
- support bundle upload after explicit approval
- project dashboard linking

A future CID SaaS connection must not support by default:

- raw video upload
- raw audio upload
- raw folder path upload
- raw filename upload
- raw transcription upload
- script upload
- dialogue upload
- automatic background media sync
- unapproved surveillance behavior

## Licensing and activation

CID Local Media Agent should have its own product licensing model.

Future licensing should consider:

- monthly subscription
- yearly subscription
- per-seat licensing
- organization licensing
- device activation
- device deactivation
- offline grace period
- license renewal
- license expiry behavior
- trial mode
- education mode
- studio mode
- anti-piracy protections without spyware or rootkit behavior

This blueprint does not implement licensing.

## Product modules

The standalone product can be organized into modules.

### Local Scanner

Purpose:

- inspect local folders
- classify media-like items
- create safe inventory
- avoid moving or deleting files

### Technical Metadata

Purpose:

- collect or simulate metadata
- use ffprobe only after explicit implementation authorization
- map errors safely
- redact unsafe outputs

### Demo Report

Purpose:

- generate stakeholder-readable local reports
- support JSON, Markdown, and HTML
- remain synthetic until authorized implementation phases

### Editing Preparation

Purpose:

- organize camera/audio candidates
- highlight review needs
- prepare assistant editor notes
- prepare DIT review notes

### Sound Preparation

Purpose:

- identify audio-like items
- flag review needs
- prepare sound department notes
- prepare future waveform sync path

### Subtitle and Transcription Preparation

Purpose:

- identify language readiness
- prepare transcription workflow
- prepare subtitle workflow
- require human review

### Export Preparation

Purpose:

- prepare future DaVinci Resolve export path
- prepare future Avid or Premiere path
- avoid claiming timeline export before implementation

## MVP product definition

The first standalone MVP should not attempt every advanced function.

The recommended MVP should include:

- local project input folder selection or CLI argument
- safe inventory
- synthetic or controlled metadata
- warning model
- review model
- suggested organization
- local JSON report
- local Markdown report
- local HTML report
- privacy statement
- limitations section
- no cloud media upload
- no file mutation

The MVP should not yet require:

- real waveform sync
- real transcription
- real subtitle translation
- real DaVinci timeline export
- real SaaS synchronization
- installer automation
- payment integration

## Commercial demo path

The first commercial-facing demo should be:

`Synthetic End-to-End Local Demo Report`

It should show:

- a local project folder label
- 10 synthetic media-like items
- safe technical metadata hints
- warning codes
- camera/audio candidate groups
- department review recommendations
- suggested folder organization
- local-only privacy confirmation
- human review requirements
- next recommended actions

The demo must be clear enough to show to editors, producers, post supervisors, schools, and trusted early customers.

## Roadmap

### Stage 1 — Standalone product definition

Status:

`IN_PROGRESS`

Goal:

- define product identity
- define independence from CID SaaS
- define local-first principles
- define licensing and packaging direction

### Stage 2 — Synthetic visible demo

Status:

`IN_PROGRESS`

Goal:

- fixture contract
- fixture QA
- fixture JSON
- report generator
- Markdown report
- HTML report

### Stage 3 — Local scanner demo

Status:

`PLANNED`

Goal:

- run local scan over controlled safe sample folder
- produce local inventory
- produce reports
- avoid file mutation

### Stage 4 — Controlled ffprobe metadata

Status:

`PLANNED`

Goal:

- safe ffprobe wrapper
- timeout handling
- metadata extraction
- stderr/stdout redaction
- local-only report

### Stage 5 — Editing intelligence

Status:

`PLANNED`

Goal:

- camera/audio grouping
- sync candidate analysis
- assistant editor report
- post supervisor report

### Stage 6 — Speech and subtitles

Status:

`PLANNED`

Goal:

- local or controlled transcription
- language detection
- subtitle readiness
- Spanish translation workflow
- human review

### Stage 7 — Packaging and licensing

Status:

`PLANNED`

Goal:

- installer strategy
- activation strategy
- offline grace
- updates
- support bundle
- commercial packaging

### Stage 8 — Private beta

Status:

`PLANNED`

Goal:

- first users
- onboarding
- feedback
- pricing validation
- support workflow
- commercial demo page

## Product risk register

### Risk 1 — Overbuilding contracts without visible demo

Mitigation:

- prioritize synthetic visible demo report
- create stakeholder-readable outputs

### Risk 2 — Weakening local-only promise

Mitigation:

- default to local reports
- require explicit authorization for SaaS sync

### Risk 3 — Trying to build full product before MVP

Mitigation:

- keep first MVP focused on inventory and reports
- defer sync, transcription, and installer automation

### Risk 4 — Confusing demo with real media analysis

Mitigation:

- label synthetic demo clearly
- separate synthetic demo from future ffprobe metadata phases

### Risk 5 — Licensing complexity too early

Mitigation:

- define licensing direction now
- implement licensing later in a dedicated phase

## Non-goals for this blueprint

This blueprint does not authorize:

- runtime code
- scanner changes
- report generation
- fixture JSON creation
- ffprobe execution
- ffmpeg execution
- transcription
- translation
- DaVinci export
- SaaS integration
- installer creation
- license server integration
- payment integration
- client media processing

## Acceptance criteria

This blueprint is accepted only if:

- CID Local Media Agent is defined as standalone product
- CID SaaS connection is optional and future-only
- local-first operation is mandatory
- video and audio uploads are prohibited by default
- product audience is defined
- MVP scope is defined
- packaging direction is defined
- licensing direction is defined
- privacy requirements are explicit
- product modules are defined
- roadmap is defined
- non-goals are explicit
- implementation remains blocked
- next phase remains gated

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.QA.GATE.V1`

After that, return to:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1`

The blueprint should guide the demo report line so the demo is built as a product demo, not only as an internal technical artifact.

## Final product decision

Product decision:

`CID_LOCAL_MEDIA_AGENT_STANDALONE_PRODUCT_BLUEPRINT_READY_FOR_QA`

CID Local Media Agent is a standalone local-first product within CID.

It may connect to CID SaaS later with customer authorization.

It must not depend on CID SaaS to work.

It must not upload customer video or audio by default.
