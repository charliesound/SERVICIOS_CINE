# CID Local Media Agent - Visible Report Runtime Generator Runtime CLI Integration Implementation Readiness QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.QA.GATE.V1`

## Objective

Validate that the runtime CLI integration implementation readiness is complete before any real CLI implementation is written.

This QA gate blocks premature CLI implementation and prevents scope creep into scanner execution, media probing, client media handling, network access, SaaS upload, database writes, or generated post-production deliverables.

This QA gate is docs/test-only.

This QA gate does not implement the CLI.

This QA gate does not modify the runtime generator.

This QA gate does not execute the scanner.

This QA gate does not use real client media.

This QA gate does not execute ffprobe or ffmpeg.

This QA gate does not perform network calls, SaaS upload, or database writes.

This QA gate does not generate synchronization, transcription, subtitles, translations, or timeline exports.

## Source Phase

Source readiness phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.V1`

Source readiness result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_PASS_READY_FOR_IMPLEMENTATION_READINESS_QA_GATE`

Source stable HEAD:

`00e6d7765cc1f8eadd8e1555fc1f55d0f4bd594e`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-implementation-readiness-v1-20260620`

## Files Under QA

This QA gate validates:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_runtime_cli_integration_implementation_readiness_v1.md`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_runtime_cli_integration_implementation_readiness.py`
- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_runtime_cli_integration_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_runtime_cli_integration_contract_qa_gate_v1.md`
- `scripts/local_media_agent/visible_report_runtime_generator.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`

## QA Gate Decision

The readiness is accepted only if the future CLI implementation remains a minimal local wrapper around the existing runtime renderer.

The future CLI must call:

`generate_visible_report(scanner_result, output_root)`

The future CLI must not duplicate renderer logic.

The future CLI must not bypass runtime validation.

The future CLI must not widen the renderer interface.

## QA Check 1 - Readiness Exists And Is Traceable

The readiness document must exist.

The readiness test must exist.

The readiness document must reference the source phase, source result, source stable HEAD, and source tag.

## QA Check 2 - Future CLI Is Still Absent

The following files must not exist during this QA gate phase:

- `scripts/local_media_agent/visible_report_runtime_cli.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`

If either file exists during this phase, the QA gate fails.

## QA Check 3 - CLI Implementation Is Still Not Authorized In This Phase

The readiness must state that this phase does not implement the CLI.

The readiness must state that it is docs/test-only.

The readiness must not create runtime CLI files.

The readiness must not modify the existing runtime generator.

## QA Check 4 - Entry Point Readiness Is Explicit

The future CLI must be prepared to expose:

`main(argv: Sequence[str] | None = None) -> int`

The future CLI must be import-safe.

Importing the future CLI module must not:

- execute rendering
- read files
- write files

## QA Check 5 - CLI Command Shape Is Locked

The future CLI command must remain equivalent to:

`python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>`

The command must require explicit arguments.

The command must not discover input implicitly.

## QA Check 6 - Required And Forbidden Flags Are Locked

The future CLI must require:

- `--scanner-result-json`
- `--output-root`

The future CLI may optionally support:

- `--dry-run`
- `--strict`
- `--print-output-path`

The future CLI must reject unsupported flags before reading input JSON.

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

## QA Check 7 - Input Readiness Is Strict

The future CLI must be ready to:

- accept only one already-created controlled scanner result JSON file
- require the JSON path to be explicit
- reject URL-like inputs
- reject mounted Windows paths
- reject Windows drive paths
- reject UNC paths
- reject repository paths as input
- reject missing files
- reject directories
- reject invalid JSON
- reject JSON roots that are not objects
- parse JSON locally
- pass parsed data to the renderer unchanged

The future CLI must not:

- scan folders
- discover input implicitly
- infer missing scanner facts
- correct invalid counts
- hide warnings
- replace invalid input with sample data
- fetch remote input

## QA Check 8 - Output Readiness Is Strict

The future CLI must be ready to:

- require an explicit output root
- delegate final report path authorization to the runtime renderer
- produce only the runtime renderer artifact
- report the created output path only after successful generation

The only expected report artifact is:

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

## QA Check 9 - Validation Order Is Locked

The future CLI implementation must validate in this order:

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

A failed step must stop execution.

A failed step must not create a report artifact.

## QA Check 10 - Failure And Success Behavior Are Locked

On failure, the future CLI must:

- return a non-zero exit code
- write a concise error to stderr
- avoid partial report writes
- avoid fallback to scanner execution
- avoid fallback to sample data
- avoid fallback to current working directory discovery
- avoid reporting success if no report was created

On success, the future CLI must:

- return exit code `0`
- create exactly one visible report artifact through the renderer
- write under `05_reports/`
- optionally print the created report path if `--print-output-path` is supplied
- avoid printing private local paths inside report content

## QA Check 11 - Future Unit Test Scope Is Ready

The future CLI implementation test must cover:

- missing required arguments
- unsupported forbidden flag
- URL-like input rejection
- unsafe input path rejection
- unsafe output root rejection
- missing JSON file
- invalid JSON
- JSON root not object
- successful delegation to `generate_visible_report`
- runtime validation error propagation
- output path print behavior
- import-safe behavior
- no planned scope creep flags

## QA Check 12 - Explicit Non-Goals Are Preserved

This QA gate must preserve these non-goals:

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

## QA Check 13 - Validation Evidence Required

The QA gate is accepted only with:

- runtime CLI integration implementation readiness test passing
- runtime CLI integration contract test passing
- runtime CLI integration contract QA gate test passing
- runtime generator test passing
- controlled runtime implementation QA gate test passing
- supporting readiness and contract tests passing
- Python compile passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing

## QA Gate Result

If all QA checks pass, the accepted result is:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_QA_GATE_PASS_READY_FOR_CONTROLLED_CLI_IMPLEMENTATION`
