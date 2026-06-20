# CID Local Media Agent - Visible Report Runtime Generator Implementation Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.V1`

## Objective

Define the exact implementation contract for the future visible report runtime generator before any runtime code is created.

This phase is docs/test-only.

This phase does not implement the runtime generator.

This phase does not create runtime report artifacts.

This phase does not create scripts, CLI commands, runtime functions, or output artifacts.

This phase does not execute the scanner.

This phase does not use real client media.

This phase does not execute ffprobe or ffmpeg.

This phase does not perform network calls, SaaS upload, or database writes.

## Source Phase

Source implementation readiness QA gate phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.READINESS.QA.GATE.V1`

Source implementation readiness QA gate result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_READINESS_QA_GATE_PASS_READY_FOR_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT`

Source stable HEAD:

`8d4f954c4572f326f664d4bbf4f7dfe986708cac`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-implementation-readiness-qa-gate-v1-20260620`

## Implementation Contract Decision

A later implementation phase may create a minimal runtime generator only if it remains local-only, deterministic, fail-closed, warning-visible, and truthful about current versus roadmap capabilities.

The implementation must be internal-demo-only until a separate future phase explicitly authorizes client-facing use.

The implementation must not expand the current Local Media Agent baseline.

## Future Module Contract

Future module name:

`visible_report_runtime_generator`

Future implementation may provide a pure rendering component that transforms validated controlled scanner result data into a producer-readable visible report.

The component must not scan folders, probe media, synchronize audio, transcribe content, generate subtitles, export timelines, upload data, write to a database, or call network services.

## Allowed Future Implementation Files

A later explicit implementation phase may introduce implementation files only under approved local-only code paths.

Potential implementation location:

- `scripts/local_media_agent/visible_report_runtime_generator.py`

Potential test location:

- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`

This contract does not create those files.

## Future Public Interface Contract

A future callable interface may be planned as:

`generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path`

The function must:

- accept already-created controlled scanner result data
- validate all required facts before rendering
- write one authorized local report artifact only after validation passes
- return the created local report path
- fail closed before writing output if validation fails

The function must not:

- execute scanner code
- execute ffprobe
- execute ffmpeg
- inspect real client media
- perform network calls
- upload to SaaS
- write to any database

## Required Future Input Schema

A later implementation must require these top-level input groups:

- `report_identity`
- `privacy_evidence`
- `scanner_summary`
- `accepted_media`
- `rejected_non_media`
- `human_review`
- `warnings`
- `created_output_artifacts`
- `roadmap_modules_not_generated`

Missing required input groups must produce a validation error and no report artifact.

## Required Future Input Facts

The implementation must validate this controlled scanner fact baseline:

- `Scanner status: completed_with_warnings`
- `Candidate media count: 5`
- `Accepted media count: 4`
- `Rejected non-media count: 3`
- `Human review required count: 1`
- `Warnings count: 1`
- `ffprobe preflight: skipped`

The implementation must not infer missing facts.

The implementation must not hide warnings.

The implementation must not silently correct inconsistent counts.

## Required Future Validation Order

A later implementation must validate in this order:

1. input object type
2. required top-level groups
3. report identity values
4. local-only privacy evidence
5. forbidden local-environment markers
6. scanner fact completeness
7. accepted and rejected media count consistency
8. human review and warning visibility
9. current-output versus roadmap-output separation
10. deterministic rendering safety
11. final output path authorization

Any failed validation step must stop rendering and prevent output creation.

## Required Future Output Contract

A later implementation may create one visible report artifact only under an explicitly authorized local output root.

The future report family remains:

- `05_reports/`

The future generator must not create or modify:

- `00_project/`
- `01_media_catalog/`
- `02_audio_sync/`
- `03_transcription/`
- `04_subtitles/`
- `06_exports/`
- database records
- SaaS records

## Required Future Report Sections

The generated visible report must preserve these 12 sections in order:

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

## Required Future Privacy Contract

The implementation must require and preserve:

- original media left client system: `false`
- SaaS upload performed: `false`
- network call performed: `false`
- database write performed: `false`

The implementation must reject any output containing:

- local user names
- machine names
- absolute system paths
- repository paths
- real client material
- real shoot names
- private project titles
- private filenames from real shoots
- `/mnt/`
- Windows drive paths
- UNC paths
- `DESKTOP-`
- `harliesound`
- `SERVICIOS_CINE`

## Required Future Determinism Contract

The implementation must produce deterministic report content for the same controlled input.

The implementation must avoid volatile metadata by default:

- wall-clock timestamps
- machine identifiers
- local absolute paths
- environment-dependent ordering

If ordering is required, the implementation must sort deterministically.

## Required Future Failure Contract

The implementation must fail closed when required data is missing, inconsistent, unsafe, or unsupported.

Allowed failure behavior:

- explicit validation exception
- no output file written
- clear human-review marker in non-client-facing diagnostic contexts
- visible warning preservation when rendering is allowed

Disallowed failure behavior:

- silent report generation after missing facts
- hiding warnings
- converting scanner candidates into finished editorial deliverables
- writing partial client-facing reports

## Explicit Non-Goals

This contract does not authorize:

- implementation in this phase
- scanner implementation changes
- scanner execution
- real media scanning
- public demo use
- client-facing demo use
- ffprobe execution
- ffmpeg execution
- waveform sync
- timecode sync
- clap sync
- transcription
- translation
- subtitle generation
- DaVinci Resolve export
- Avid export
- SaaS upload
- database writes
- network calls
- Docker or Alembic changes
- frontend/backend SaaS changes
- Stripe, AI Jobs, credits, or ledger changes

## Implementation Contract Acceptance Criteria

The implementation contract is accepted only if it defines a minimal, local-only, deterministic, fail-closed rendering component that can be implemented later without expanding current product claims.

The contract must preserve the boundary between scanner facts, visible report rendering, and roadmap-only modules.

## Result

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_IMPLEMENTATION_CONTRACT_QA_GATE`

## Next Recommended Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.QA.GATE.V1`
