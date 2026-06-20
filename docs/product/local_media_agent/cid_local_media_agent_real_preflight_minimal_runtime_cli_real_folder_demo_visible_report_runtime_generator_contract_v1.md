# CID Local Media Agent - Visible Report Runtime Generator Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.V1`

## Objective

Define the contract for a future runtime generator that will create the internal demo visible report automatically from controlled local scanner outputs.

This phase is docs/test-only.

This phase does not implement the runtime generator.

This phase does not execute the scanner.

This phase does not modify scanner code.

This phase does not generate a runtime report.

This phase does not use real client media.

## Source Phase

Source static fixture QA gate phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.FIXTURE.QA.GATE.V1`

Source result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_STATIC_FIXTURE_QA_GATE_PASS_READY_FOR_RUNTIME_REPORT_GENERATOR_CONTRACT`

Source stable HEAD:

`33e0ace78cd78c61cd14884c6b549a6ed47a8b6e`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-static-fixture-qa-gate-v1-20260620`

## Runtime Generator Status

Runtime generator implemented: `false`

Runtime generator execution allowed in this phase: `false`

Runtime visible report output generated in this phase: `false`

Scanner execution allowed in this phase: `false`

Real client media allowed in this phase: `false`

## Generator Purpose

The future generator will transform controlled local scanner result data into a producer-readable visible report.

The report must remain truthful about the current Local Media Agent baseline.

The report must show what the scanner did, what it rejected, what requires human review, what warnings exist, and what modules are still roadmap-only.

The report must not present future modules as current capabilities.

## Expected Future Inputs

The future generator may consume controlled local-only inputs such as:

- scanner summary data
- accepted media candidates
- rejected non-media entries
- human review flags
- warning records
- output artifact inventory
- local-only privacy evidence

The future generator must not require:

- network access
- SaaS upload
- database writes
- real client media outside an explicitly authorized future phase
- ffprobe execution unless a later explicit phase authorizes it
- ffmpeg execution unless a later explicit phase authorizes it

## Expected Future Outputs

The future generator may eventually create visible report artifacts under the roadmap output family:

- `05_reports/`

The primary future artifact should be a human-readable internal report.

The future artifact must preserve the same visible report structure used by the static fixture.

This contract does not create the `05_reports/` runtime output.

## Required Visible Report Sections

The future generated report must contain these 12 sections in order:

1. `Executive Summary`
2. `Local-Only Privacy Confirmation`
3. `Controlled Demo Input Summary`
4. `Scanner Result Summary`
5. `Accepted Media`
6. `Rejected Non-Media`
7. `Human Review Required`
8. `Warnings`
9. `Created Output Artifacts`
10. `Roadmap Modules Not Yet Generated`
11. `Producer Interpretation`
12. `Next Technical Actions`

## Required Report Identity Fields

The future generated report must expose:

- report title
- report audience
- report status
- privacy mode
- scenario identifier
- generator mode
- runtime generation status
- real client media usage status

For the controlled demo baseline, these values must remain equivalent to:

- `CID Local Media Agent - Internal Demo Visible Report`
- `producer_product_post_internal_review`
- `internal_demo_only`
- `local_only`
- `approved_synthetic_controlled_demo`
- `runtime_generated` only after a later implementation phase exists
- `real client media used: false`

## Required Scanner Fact Mapping

For the current controlled demo baseline, the future generated report must preserve these scanner facts:

- `Scanner status: completed_with_warnings`
- `Candidate media count: 5`
- `Accepted media count: 4`
- `Rejected non-media count: 3`
- `Human review required count: 1`
- `Warnings count: 1`
- `ffprobe preflight: skipped`

The generator must fail closed or surface a validation warning if required scanner facts are missing.

## Required Media Interpretation

Accepted media must be represented as scanner candidates only.

For the current controlled demo baseline, accepted media must include:

- `.mov = 1`
- `.mp4 = 2`
- `.wav = 1`

Rejected non-media must include:

- `.exe = 1`
- `.txt = 2`

The future generated report must clearly state that accepted media are not synchronized clips, transcribed clips, subtitled clips, edited deliverables, or exported timelines.

## Human Review and Warning Requirements

The future generated report must keep human review visible when ambiguity exists.

For the current controlled demo baseline, it must include:

- `Human review required: true`
- `Human review reason: unknown synthetic placeholder`
- `Warning count: 1`
- `Warning detail: unknown synthetic placeholder`
- `Warning severity: controlled_demo_warning`

Warnings must not be hidden to make the demo appear cleaner.

## Local-Only Privacy Requirements

The future generator must preserve local-only privacy guarantees.

The generated report must state:

- original media left client system: `false`
- SaaS upload performed: `false`
- network call performed: `false`
- database write performed: `false`

The generated report must not expose:

- local user names
- machine names
- absolute system paths
- repository paths
- real client material
- real shoot names
- private project titles
- private filenames from real shoots

The generated report must not contain forbidden local-environment markers such as:

- `/mnt/`
- Windows drive paths
- UNC paths
- `DESKTOP-`
- `harliesound`
- `SERVICIOS_CINE`

## Current Outputs vs Roadmap Outputs

The future generated report must present only these output families as current baseline outputs:

- `00_project/`
- `01_media_catalog/`
- `99_logs/`

The future generated report must keep these output families as roadmap-only until explicitly implemented:

- `02_audio_sync/`
- `03_transcription/`
- `04_subtitles/`
- `05_reports/`
- `06_exports/`

The generator must not claim that the current baseline creates audio synchronization outputs, transcription outputs, subtitle outputs, translation outputs, DaVinci Resolve exports, or Avid exports.

## Determinism Requirement

Given the same controlled local scanner input, the future generator must produce the same visible report content except for explicitly approved volatile metadata.

Approved volatile metadata must be avoided in the controlled demo report unless a later phase explicitly allows it.

Examples of volatile metadata that should be avoided by default:

- wall-clock timestamps
- machine identifiers
- local absolute paths
- environment-dependent ordering

## Failure Behavior

The future generator must fail closed when required data is missing or unsafe.

The generator must not silently create a polished report if scanner facts, warning records, or privacy evidence are incomplete.

Acceptable failure behavior includes:

- explicit validation error
- visible warning section
- human review required marker
- refusal to generate a client-facing artifact

## Contract Boundary

This contract does not authorize:

- runtime report generator implementation
- scanner implementation changes
- real media scanning
- public demo use
- client-facing demo use
- ffprobe execution
- ffmpeg execution
- SaaS upload
- database writes
- network calls
- Docker or Alembic changes
- frontend/backend SaaS changes
- Stripe, AI Jobs, credits, or ledger changes

## Acceptance Criteria

The runtime generator contract is accepted only if it defines how a future generator will create a visible report while preserving:

- local-only privacy
- controlled synthetic demo boundaries
- current scanner baseline truthfulness
- producer-readable report structure
- clear distinction between current outputs and roadmap modules
- fail-closed behavior for missing or unsafe data

## Result

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTRACT_PASS_READY_FOR_QA_GATE`

## Next Recommended Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.QA.GATE.V1`
