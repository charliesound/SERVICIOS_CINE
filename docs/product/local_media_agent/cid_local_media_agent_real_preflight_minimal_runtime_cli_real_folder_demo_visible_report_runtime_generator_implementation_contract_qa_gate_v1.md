# CID Local Media Agent - Visible Report Runtime Generator Implementation Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.QA.GATE.V1`

## Objective

Validate that the visible report runtime generator implementation contract is safe, complete, local-only, deterministic, fail-closed, warning-visible, and ready for a later implementation phase.

This phase is docs/test-only.

This phase does not implement the runtime generator.

This phase does not create runtime report artifacts.

This phase does not create scripts, CLI commands, runtime functions, or output artifacts.

This phase does not execute the scanner.

This phase does not use real client media.

This phase does not execute ffprobe or ffmpeg.

This phase does not perform network calls, SaaS upload, or database writes.

## Source Phase

Source implementation contract phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.V1`

Source implementation contract result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_IMPLEMENTATION_CONTRACT_QA_GATE`

Source stable HEAD:

`8fcb79a1289a43809b74392e9783ca34db1090f8`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-implementation-contract-v1-20260620`

## Files Under QA

This QA gate validates:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_contract.py`

## QA Gate Decision

The implementation contract is accepted only if it preserves all safety, privacy, deterministic rendering, fail-closed behavior, and non-goal boundaries required before code implementation.

This QA gate authorizes only a later implementation-readiness-to-code transition.

This QA gate does not authorize runtime code in this phase.

## QA Check 1 - Contract Remains Docs/Test Only

The contract must prove that the implementation contract phase remains docs/test-only.

Required evidence:

- no runtime generator implementation
- no runtime report artifacts
- no scripts created
- no CLI commands created
- no runtime functions created
- no output artifacts created
- no scanner execution
- no real client media
- no ffprobe execution
- no ffmpeg execution
- no network calls
- no SaaS upload
- no database writes

## QA Check 2 - Source Traceability Is Complete

The contract must preserve source traceability to:

- source phase
- source result
- source stable HEAD
- source tag
- previous implementation readiness QA gate
- previous implementation readiness contract

Required source HEAD:

`8fcb79a1289a43809b74392e9783ca34db1090f8`

Required source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-implementation-contract-v1-20260620`

## QA Check 3 - Implementation Decision Is Properly Limited

The contract must state that a later implementation phase may create only a minimal runtime generator.

The generator must remain:

- local-only
- deterministic
- fail-closed
- warning-visible
- truthful about current versus roadmap capabilities
- internal-demo-only until separately authorized

The contract must state that the implementation must not expand the current Local Media Agent baseline.

## QA Check 4 - Future Module Contract Is Explicit

The future module name must remain:

`visible_report_runtime_generator`

The future component must be a pure rendering component.

The component may only transform validated controlled scanner result data into a producer-readable visible report.

The component must not:

- scan folders
- probe media
- synchronize audio
- transcribe content
- generate subtitles
- export timelines
- upload data
- write to a database
- call network services

## QA Check 5 - Future Implementation Files Are Planned But Not Created

The contract may plan these future implementation files:

- `scripts/local_media_agent/visible_report_runtime_generator.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`

The contract must state that those files are not created in the contract phase.

The repository must not contain those future runtime implementation files in this QA gate phase.

## QA Check 6 - Future Public Interface Is Narrow

The planned interface must remain:

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

## QA Check 7 - Required Future Input Schema Is Complete

The contract must require these input groups:

- `report_identity`
- `privacy_evidence`
- `scanner_summary`
- `accepted_media`
- `rejected_non_media`
- `human_review`
- `warnings`
- `created_output_artifacts`
- `roadmap_modules_not_generated`

Missing required input groups must produce validation error and no report artifact.

## QA Check 8 - Required Scanner Fact Baseline Is Preserved

The contract must preserve this controlled scanner fact baseline:

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

## QA Check 9 - Required Future Validation Order Is Complete

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

## QA Check 10 - Future Output Contract Is Local And Limited

The contract must allow only one visible report artifact under an explicitly authorized local output root.

The future report family must remain:

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

## QA Check 11 - Required Future Report Sections Are Preserved

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

## QA Check 12 - Privacy Contract Is Strict

The future implementation must require and preserve:

- original media left client system: `false`
- SaaS upload performed: `false`
- network call performed: `false`
- database write performed: `false`

The implementation must reject output containing:

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

## QA Check 13 - Determinism Contract Is Strict

The implementation must produce deterministic report content for the same controlled input.

The implementation must avoid volatile metadata by default:

- wall-clock timestamps
- machine identifiers
- local absolute paths
- environment-dependent ordering

If ordering is required, the implementation must sort deterministically.

## QA Check 14 - Failure Contract Is Fail-Closed

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

## QA Check 15 - Explicit Non-Goals Block Scope Creep

The contract must not authorize:

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

## QA Check 16 - Acceptance Criteria Are Implementation-Safe

The implementation contract is accepted only if it defines a minimal, local-only, deterministic, fail-closed rendering component that can be implemented later without expanding current product claims.

The contract must preserve the boundary between:

- scanner facts
- visible report rendering
- roadmap-only modules

## QA Gate Acceptance Criteria

This QA gate passes only if all checks confirm that the implementation contract is ready for a later controlled implementation phase without allowing runtime code in this QA gate phase.

This QA gate must keep the runtime generator unimplemented.

This QA gate must keep the Local Media Agent local-only and private.

This QA gate must prevent over-claiming of sync, transcription, subtitles, exports, SaaS integration, or client-facing demo readiness.

## Result

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_QA_GATE_PASS_READY_FOR_CONTROLLED_RUNTIME_IMPLEMENTATION`

## Next Recommended Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.RUNTIME.IMPLEMENTATION.V1`
