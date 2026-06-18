# CID Local Media Agent — Status Roadmap Audit v1

## Phase

`CID.LOCAL_MEDIA_AGENT.STATUS.ROADMAP.AUDIT.V1`

## Objective

This audit reviews the current state of CID Local Media Agent after the scanner, ffprobe, failure path, command wrapper, and test double contract phases.

The purpose is to separate what is already stable from what is still only contractual, identify the remaining gaps toward a functional local demo, and provide an effort roadmap toward a commercial beta.

This phase is documentation/test-only. It does not implement runtime behavior, does not execute ffprobe, does not execute ffmpeg, does not add subprocess usage, does not scan real media, and does not modify scanner runtime.

## Current repository state audited

Current stable HEAD before this audit:

`a1db7dc`

Current latest closed Local Media Agent phase:

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.V1`

The repository contains a broad Local Media Agent foundation covering product definition, data contracts, local output contracts, scanner CLI contracts, safe baseline, execution hardening, path privacy, ffprobe contracts, metadata schema, synthetic fixtures, placeholders, failure paths, command wrapper contracts, test double contracts, readiness gates, and implementation planning.

## What is already strong

The current state is strong in:

- local-only product positioning
- privacy-by-design constraints
- no cloud upload of client media
- scanner CLI contract design
- local output contract design
- media project data contract design
- test fixture policy
- safe baseline documentation
- path policy and privacy edge cases
- ffprobe availability planning
- ffprobe metadata schema planning
- synthetic probe planning
- synthetic fixture and placeholder planning
- failure path vocabulary
- failure path QA
- command wrapper contract
- command wrapper QA
- implementation readiness gates
- test double contract
- test double QA
- minimal implementation planning

This means the product has a solid safety and design base before touching media or external binaries.

## What is not yet functional

The current state must not be mistaken for a working commercial tool.

As of this audit, the Local Media Agent line still does not have a confirmed functional end-to-end demo that performs all of these operations on real client-style media:

- real folder scan with full media classification
- real ffprobe execution
- real technical metadata extraction
- real video/audio duration reporting
- real audio channel and sample-rate reporting
- real codec/container inspection
- real media error handling from external binaries
- real waveform sync
- real timecode sync
- real slate/clap detection
- real transcription
- real speaker/language segmentation
- real subtitle generation
- real Spanish translation workflow
- real DaVinci Resolve export
- real Avid export
- real installer
- real licensing or activation
- real customer beta workflow

The current state is therefore best classified as:

`ARCHITECTURE_AND_SAFETY_FOUNDATION_READY`

It is not yet:

`FUNCTIONAL_LOCAL_DEMO_READY`

It is not yet:

`COMMERCIAL_BETA_READY`

## Product level assessment

### Level 1 — Architecture and safety foundation

Status:

`MOSTLY_READY`

Evidence:

- product spec exists
- local-only policy exists
- data contracts exist
- scanner contracts exist
- ffprobe contracts exist
- failure paths exist
- wrapper contracts exist
- test double planning exists
- safety guards are consistently used

### Level 2 — Synthetic local prototype

Status:

`PARTIALLY_READY`

Missing:

- minimal test double implementation
- synthetic command runner result objects
- synthetic success and failure outputs wired into tests
- local demo report generated from synthetic data
- visible demo artifact for a non-technical stakeholder

### Level 3 — Functional local scanner demo

Status:

`NOT_YET_READY`

Missing:

- confirmed CLI path for demo execution
- stable local project input folder convention
- safe local output folder convention
- end-to-end inventory report
- HTML or Markdown demo report
- fixture-based demo command
- validation that no sensitive paths leak

### Level 4 — ffprobe real metadata demo

Status:

`NOT_YET_READY`

Missing:

- explicit authorization gate for real ffprobe execution
- safe command wrapper implementation
- timeout handling
- stdout and stderr redaction
- JSON parsing and failure mapping
- media-type filtering
- local-only reporting
- controlled non-client sample media policy

### Level 5 — Editing Intelligence demo

Status:

`NOT_YET_READY`

Missing:

- clip grouping
- video/audio pairing heuristics
- sync candidate model
- timecode analysis
- waveform sync research and implementation
- slate/clap detection strategy
- transcription strategy
- subtitle and translation strategy
- DaVinci Resolve export design
- review UI or report for editor/assistant editor

### Level 6 — Private beta product

Status:

`NOT_YET_READY`

Missing:

- installer strategy
- dependency bundling strategy
- license/activation model
- customer onboarding flow
- support and logging policy
- crash/error report policy
- performance tests on large folders
- privacy and legal text
- commercial demo material

## Recommended next build path

The fastest safe route toward a visible demo is not to jump directly to waveform sync or transcription.

Recommended path:

1. Finish test double plan QA.
2. Implement a minimal pure test double in test support only.
3. Build a synthetic end-to-end demo report.
4. Build a local scanner demo using synthetic or harmless placeholder files.
5. Add controlled ffprobe execution behind a separate authorization gate.
6. Generate a real local technical metadata report from non-client sample media.
7. Convert that report into a commercial-facing HTML demo.
8. Only then move toward sync, transcription, subtitle, and DaVinci export.

## Practical roadmap

### Block A — Finish synthetic foundation

Goal:

`SYNTHETIC_DEMO_FOUNDATION_READY`

Main work:

- test double plan QA
- minimal test double implementation
- minimal test double QA
- synthetic result fixtures
- synthetic report contract
- synthetic end-to-end demo report

Estimated effort:

`SMALL_TO_MEDIUM`

Expected value:

This gives a safe visible demo without external binaries or real media.

### Block B — Local scanner demo

Goal:

`LOCAL_SCANNER_DEMO_READY`

Main work:

- demo input folder convention
- demo output folder convention
- scanner command documentation
- local JSON report
- local Markdown or HTML report
- privacy leak checks
- demo runbook

Estimated effort:

`MEDIUM`

Expected value:

This becomes the first thing that can be shown as a working local tool.

### Block C — Controlled ffprobe metadata

Goal:

`CONTROLLED_FFPROBE_METADATA_DEMO_READY`

Main work:

- explicit execution authorization gate
- safe wrapper implementation
- timeout handling
- failure path mapping
- metadata parser
- redacted local report
- tests with controlled sample media or synthetic subprocess boundary

Estimated effort:

`MEDIUM_TO_HIGH`

Expected value:

This starts making the tool genuinely useful for postproduction.

### Block D — Editing workflow intelligence

Goal:

`EDITING_INTELLIGENCE_DEMO_READY`

Main work:

- clip grouping
- media organization suggestions
- camera/audio pairing candidates
- timecode sync analysis
- waveform sync research
- slate/clap strategy
- export planning for DaVinci Resolve

Estimated effort:

`HIGH`

Expected value:

This is the first version that feels like a real assistant for editor, assistant editor, DIT, sound, or post supervisor.

### Block E — Speech, subtitles, translation

Goal:

`TRANSCRIPTION_SUBTITLE_DEMO_READY`

Main work:

- local transcription model strategy
- language detection
- speaker/segment model
- subtitle generation
- Spanish translation workflow
- human review policy
- export formats

Estimated effort:

`HIGH`

Expected value:

This makes the product commercially attractive for documentary, interviews, archive, and multilingual postproduction.

### Block F — Beta packaging

Goal:

`PRIVATE_BETA_READY`

Main work:

- installer strategy
- dependency checks
- local configuration
- customer license model
- activation policy
- offline grace policy
- support documentation
- onboarding checklist
- demo video and landing

Estimated effort:

`HIGH`

Expected value:

This makes the tool sellable as a private beta.

## Effort estimate in practical terms

The current work is approximately at:

`FOUNDATION 35-45% OF A LOCAL DEMO`

But only around:

`10-15% OF A COMMERCIAL PRIVATE BETA`

Reason:

The safety, privacy, contracts, and QA foundations are strong, but the user-visible functional layers still remain mostly unbuilt.

The most realistic next milestone is:

`SYNTHETIC_LOCAL_DEMO`

Then:

`CONTROLLED_LOCAL_METADATA_DEMO`

Then:

`COMMERCIAL_PRIVATE_BETA`

## Recommended immediate next phase

The immediate next phase should be:

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.QA.GATE.V1`

After that, the next audit-driven phase should be:

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.READINESS.GATE.V1`

Only after that should any minimal test double code be considered.

## Strategic recommendation

Do not continue adding many more abstract contracts before creating something visible.

After the current test double line is safely closed, the product should pivot toward:

`SYNTHETIC END-TO-END LOCAL DEMO REPORT`

The demo should show:

- input folder
- detected media-like items
- synthetic technical metadata
- safe labels
- warnings
- suggested organization
- local output report
- zero cloud upload

This will help communicate the product to editors, post supervisors, producers, and possible first customers much better than more internal contracts.

## Commercial message to validate

The commercial demo should communicate:

"CID Local Media Agent analiza una carpeta local de material audiovisual sin subir vídeos ni audios a la nube y genera una radiografía técnica y editorial para preparar montaje, sonido, subtítulos y postproducción."

## Final audit decision

Audit decision:

`CONTINUE_BUT_PIVOT_TOWARD_VISIBLE_SYNTHETIC_DEMO`

The current foundation is safe enough to continue.

The next work should avoid unnecessary abstraction and move toward a visible local demo while keeping privacy and local-only constraints intact.
