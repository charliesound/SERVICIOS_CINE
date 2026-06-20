# CID Local Media Agent - Visible Report Runtime Generator Controlled CLI Implementation QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.CLI.IMPLEMENTATION.QA.GATE.V1`

## Objective

Validate the controlled CLI implementation for the visible report runtime generator.

This QA gate confirms that the implemented CLI is a minimal local wrapper around the existing runtime renderer.

The CLI must read one controlled scanner result JSON file, validate paths and JSON shape, delegate to the renderer, and create only the visible report artifact under the authorized output root.

## Source Phase

Source implementation phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTROLLED.CLI.IMPLEMENTATION.V1`

Source implementation result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_IMPLEMENTATION_PASS_READY_FOR_CONTROLLED_CLI_IMPLEMENTATION_QA_GATE`

Source stable HEAD:

`7093d22c0a1a2be45cec4a262acee40d52c98afa`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-cli-implementation-v1-20260620`

## Files Under QA

This QA gate validates:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_implementation_v1.md`
- `scripts/local_media_agent/visible_report_runtime_cli.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`
- `scripts/local_media_agent/visible_report_runtime_generator.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`

## QA Check 1 - CLI Exists

The controlled CLI implementation file must exist:

- `scripts/local_media_agent/visible_report_runtime_cli.py`

The controlled CLI implementation test must exist:

- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`

## QA Check 2 - CLI Entry Point Is Narrow

The CLI must expose:

`main(argv: Sequence[str] | None = None) -> int`

The CLI module must remain import-safe.

Importing the CLI module must not execute rendering.

Importing the CLI module must not read input files.

Importing the CLI module must not write output files.

## QA Check 3 - Renderer Delegation Is Preserved

The CLI must delegate rendering to:

`generate_visible_report(scanner_result, output_root)`

The CLI must not duplicate renderer logic.

The CLI must not bypass runtime validation.

The CLI must not widen the renderer interface.

## QA Check 4 - Arguments Remain Controlled

The CLI must require:

- `--scanner-result-json`
- `--output-root`

The CLI may support:

- `--dry-run`
- `--strict`
- `--print-output-path`

The CLI must reject unsupported flags before reading input JSON.

## QA Check 5 - Forbidden Flags Remain Blocked

The CLI must reject:

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

## QA Check 6 - Input Safety Is Enforced

The CLI must reject:

- URL-like inputs
- mounted Windows paths
- Windows drive paths
- UNC paths
- repository paths as input
- missing files
- directories
- invalid JSON
- JSON roots that are not objects

The CLI must parse JSON locally.

The CLI must pass the parsed object to the renderer unchanged.

## QA Check 7 - Output Safety Is Enforced

The CLI must require an explicit output root.

The CLI must reject unsafe output roots.

The CLI must delegate final report path authorization to the runtime renderer.

The expected artifact remains:

`05_reports/cid_local_media_agent_visible_report_v1.md`

## QA Check 8 - Failure Behavior Is Controlled

On failure, the CLI must:

- return a non-zero exit code
- write a concise error to stderr
- not report success
- not fall back to scanner execution
- not fall back to sample data
- not discover inputs from the current working directory

## QA Check 9 - Success Behavior Is Controlled

On success, the CLI must:

- return exit code `0`
- delegate one render operation to the runtime renderer
- optionally print the created report path when `--print-output-path` is supplied
- avoid writing outputs directly outside renderer control

## QA Check 10 - Dry Run Behavior Is Controlled

When `--dry-run` is supplied, the CLI must validate arguments and JSON shape without invoking the renderer and without creating report artifacts.

## QA Check 11 - Non-Goals Remain Preserved

This QA gate does not authorize:

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

## QA Check 12 - Validation Evidence Required

The QA gate is accepted only with:

- controlled CLI implementation test passing
- runtime generator test passing
- controlled runtime implementation QA gate test passing
- supporting implemented runtime chain tests passing
- Python compile passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing

## QA Gate Result

If all QA checks pass, the accepted result is:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_IMPLEMENTATION_QA_GATE_PASS_READY_FOR_CONTROLLED_CLI_EXECUTION`
