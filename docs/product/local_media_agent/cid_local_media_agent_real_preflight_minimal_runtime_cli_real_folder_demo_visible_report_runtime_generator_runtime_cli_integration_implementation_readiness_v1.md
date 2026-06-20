# CID Local Media Agent - Visible Report Runtime Generator Runtime CLI Integration Implementation Readiness v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.V1`

## Objective

Prepare the future implementation of the local runtime CLI wrapper for the visible report generator.

This readiness phase confirms that the next implementation can safely create a minimal CLI entry point that invokes the existing renderer without expanding scope.

This phase is docs/test-only.

This phase does not implement the CLI.

This phase does not modify the runtime generator.

This phase does not execute the scanner.

This phase does not use real client media.

This phase does not execute ffprobe or ffmpeg.

This phase does not perform network calls, SaaS upload, or database writes.

This phase does not generate synchronization, transcription, subtitles, translations, or timeline exports.

## Source Phase

Source QA gate phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.QA.GATE.V1`

Source QA gate result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS`

Source stable HEAD:

`028088a77322ca3f3dfb14dcccf44bd9db7a501a`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-contract-qa-gate-v1-20260620`

## Existing Runtime Dependency

The future CLI implementation must call:

`generate_visible_report(scanner_result, output_root)`

from:

- `scripts/local_media_agent/visible_report_runtime_generator.py`

The CLI must not duplicate renderer logic.

The CLI must not bypass runtime validation.

The CLI must not widen the renderer interface.

## Planned Implementation Files

A later explicit implementation phase may create:

- `scripts/local_media_agent/visible_report_runtime_cli.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`

This readiness phase must not create those files.

If either planned CLI file already exists during this readiness phase, readiness fails.

## Future CLI Entry Point

The future CLI implementation must provide a local command equivalent to:

`python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>`

The CLI must expose a callable `main(argv: Sequence[str] | None = None) -> int`.

The CLI may expose a small argument parser helper if needed.

The CLI must be import-safe.

Importing the CLI module must not execute rendering.

Importing the CLI module must not read files.

Importing the CLI module must not write files.

## Required Arguments

The future CLI must require:

- `--scanner-result-json`
- `--output-root`

The future CLI may optionally support:

- `--dry-run`
- `--strict`
- `--print-output-path`

The future CLI must reject unsupported flags before reading input JSON.

## Forbidden Flags

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

## Input Readiness Requirements

The future CLI implementation must:

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

The CLI must not:

- scan folders
- discover input implicitly
- infer missing scanner facts
- correct invalid counts
- hide warnings
- replace invalid input with sample data
- fetch remote input

## Output Readiness Requirements

The future CLI implementation must:

- require an explicit output root
- delegate final report path authorization to the runtime renderer
- produce only the runtime renderer artifact
- report the created output path only after successful generation

The only expected report artifact is:

- `05_reports/cid_local_media_agent_visible_report_v1.md`

The CLI must not create or modify:

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

## Required Future Validation Order

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

## Failure Behavior Readiness

The future CLI must return a non-zero exit code for failures.

The future CLI must write a concise error to stderr for failures.

The future CLI must not write a partial report.

The future CLI must not fall back to scanner execution.

The future CLI must not fall back to sample data.

The future CLI must not fall back to current working directory discovery.

The future CLI must not report success if no report was created.

## Success Behavior Readiness

On success, the future CLI must:

- return exit code `0`
- create exactly one visible report artifact through the renderer
- write under `05_reports/`
- optionally print the created report path if `--print-output-path` is supplied
- avoid printing private local paths inside report content

## Future Unit Test Readiness

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

## Explicit Non-Goals

This readiness phase does not authorize:

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

## Readiness Decision

The future CLI implementation is ready to proceed only if:

- current repo state is clean before implementation
- future CLI file is still absent
- future CLI test file is still absent
- runtime CLI integration contract test passes
- runtime CLI integration contract QA gate test passes
- runtime generator test passes
- controlled runtime implementation QA gate test passes
- supporting readiness and contract tests pass
- WSL/repo guard passes
- database backend regression guard passes

## Readiness Result

If all readiness checks pass, the accepted result is:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_PASS_READY_FOR_IMPLEMENTATION_READINESS_QA_GATE`
