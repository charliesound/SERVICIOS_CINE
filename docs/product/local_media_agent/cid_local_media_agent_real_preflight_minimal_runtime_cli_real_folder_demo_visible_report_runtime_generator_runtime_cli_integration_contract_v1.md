# CID Local Media Agent - Visible Report Runtime Generator Runtime CLI Integration Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.V1`

## Objective

Define the future CLI integration contract for invoking the controlled visible report runtime generator from a command-line entry point.

This phase is docs/test-only.

This phase does not implement a CLI command.

This phase does not modify the existing runtime generator.

This phase does not execute the scanner.

This phase does not use real client media.

This phase does not execute ffprobe or ffmpeg.

This phase does not perform network calls, SaaS upload, or database writes.

This phase does not generate synchronization, transcription, subtitles, or timeline exports.

## Source Phase

Source QA gate phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.RUNTIME.IMPLEMENTATION.QA.GATE.V1`

Source QA gate result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_RUNTIME_IMPLEMENTATION_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT`

Source stable HEAD:

`1bf737f9b04eb785944733fa7b6ae267ce1db045`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-runtime-implementation-qa-gate-v1-20260620`

## Existing Runtime Under Contract

The future CLI integration must call the existing renderer through the narrow interface:

`generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path`

Runtime generator file:

- `scripts/local_media_agent/visible_report_runtime_generator.py`

Existing runtime test:

- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`

Existing runtime QA gate:

- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_runtime_implementation_qa_gate.py`

## Future CLI File Contract

A later explicit implementation phase may introduce a CLI file only under an approved local-only code path.

Planned CLI file:

- `scripts/local_media_agent/visible_report_runtime_cli.py`

Planned CLI test file:

- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`

This contract does not create those files.

## Future CLI Command Shape

The future CLI may expose a local command with this conceptual shape:

`python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>`

The command must require explicit arguments.

The command must not use implicit current working directory input discovery.

The command must not scan folders.

The command must not probe media.

The command must not fetch remote input.

The command must not accept URLs.

The command must not accept SaaS identifiers.

The command must not read environment secrets.

## Required Future CLI Arguments

The future CLI must require:

- `--scanner-result-json`
- `--output-root`

The future CLI may support:

- `--dry-run`
- `--strict`
- `--print-output-path`

The future CLI must not support:

- `--scan`
- `--ffprobe`
- `--ffmpeg`
- `--sync`
- `--transcribe`
- `--subtitle`
- `--export-davinci`
- `--export-avid`
- `--upload`
- `--database-write`
- `--network`
- `--client-facing`

## Required Future CLI Input Contract

The future CLI must accept only an already-created controlled scanner result JSON file.

The future CLI must parse JSON locally.

The future CLI must pass parsed data to:

`generate_visible_report(scanner_result, output_root)`

The future CLI must not:

- mutate scanner result data
- infer missing facts
- silently correct invalid counts
- hide warnings
- convert roadmap modules into generated deliverables

## Required Future CLI Output Contract

The future CLI may create only the one visible report artifact created by the runtime generator:

- `05_reports/cid_local_media_agent_visible_report_v1.md`

The future CLI must not create or modify:

- `00_project/`
- `01_media_catalog/`
- `02_audio_sync/`
- `03_transcription/`
- `04_subtitles/`
- `06_exports/`
- database records
- SaaS records
- scanner outputs
- media derivatives

## Required Future CLI Validation Order

A later CLI implementation must validate in this order:

1. CLI argument presence
2. unsupported flag rejection
3. input JSON path safety
4. output root path safety
5. JSON file existence
6. JSON parse success
7. parsed object type
8. delegation to `generate_visible_report`
9. runtime validation result
10. final output path reporting

Any failed validation step must stop execution and prevent report artifact creation.

## Required Future CLI Failure Contract

The future CLI must fail closed when:

- required arguments are missing
- unsupported flags are provided
- input path is unsafe
- output path is unsafe
- JSON is missing
- JSON is invalid
- JSON root is not an object
- runtime generator validation fails
- output path is not authorized

Allowed failure behavior:

- non-zero process return code
- concise stderr error
- no report artifact written

Disallowed failure behavior:

- partial report writes
- fallback to scanner execution
- fallback to sample data
- fallback to current working directory discovery
- silent success
- client-facing report claims

## Required Future Privacy Contract

The future CLI must preserve the runtime privacy contract.

The future CLI must not allow output content containing:

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

The future CLI must be deterministic for the same controlled JSON input and output root.

The CLI must not inject:

- wall-clock timestamps
- machine identifiers
- local absolute paths into report content
- environment-dependent ordering

The runtime renderer remains responsible for deterministic Markdown content.

## Explicit Non-Goals

This contract does not authorize:

- CLI implementation in this phase
- scanner execution
- scanner implementation changes
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
- frontend/backend SaaS changes

## Contract Result

If this contract is accepted, the result is:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE`
