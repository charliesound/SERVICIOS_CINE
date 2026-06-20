# CID Local Media Agent - Visible Report Runtime Generator Controlled CLI Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTROLLED.CLI.IMPLEMENTATION.V1`

## Objective

Implement the minimal local CLI wrapper for the visible report runtime generator.

The CLI reads one already-created controlled scanner result JSON file, validates paths and JSON shape, delegates rendering to the existing runtime renderer, and optionally prints the generated report path.

## Source Phase

Source QA gate phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.QA.GATE.V1`

Source QA gate result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_QA_GATE_PASS_READY_FOR_CONTROLLED_CLI_IMPLEMENTATION`

Source stable HEAD:

`bbf4a040a97ebf6512cd15454880ff2bef750450`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-implementation-readiness-qa-gate-v1-20260620`

## Implemented Files

This phase creates:

- `scripts/local_media_agent/visible_report_runtime_cli.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`

## CLI Command

The implemented command is:

`python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>`

## Public Entry Point

The CLI exposes:

`main(argv: Sequence[str] | None = None) -> int`

The module is import-safe.

Importing the module does not execute rendering.

Importing the module does not read input files.

Importing the module does not write output files.

## Required Arguments

The CLI requires:

- `--scanner-result-json`
- `--output-root`

## Optional Arguments

The CLI supports:

- `--dry-run`
- `--strict`
- `--print-output-path`

`--strict` is accepted as a reserved compatibility flag for the controlled CLI contract. It does not widen runtime behavior.

## Forbidden Flags

The CLI rejects these flags before reading input JSON:

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

## Input Behavior

The CLI accepts only one already-created controlled scanner result JSON file.

The CLI rejects:

- URL-like inputs
- mounted Windows paths
- Windows drive paths
- UNC paths
- repository paths as input
- missing files
- directories
- invalid JSON
- JSON roots that are not objects

The CLI parses JSON locally and passes the parsed object to the renderer unchanged.

## Output Behavior

The CLI requires an explicit output root.

The CLI delegates final report path authorization to:

`generate_visible_report(scanner_result, output_root)`

The expected report artifact remains:

`05_reports/cid_local_media_agent_visible_report_v1.md`

The CLI does not create scanner outputs, media derivatives, database records, or SaaS records.

## Failure Behavior

On failure, the CLI:

- returns a non-zero exit code
- writes a concise error to stderr
- does not create a partial report intentionally
- does not fall back to scanner execution
- does not fall back to sample data
- does not discover inputs from the current working directory

## Success Behavior

On success, the CLI:

- returns exit code `0`
- delegates exactly one render operation to the runtime renderer
- writes only through the renderer
- optionally prints the created report path when `--print-output-path` is supplied

## Explicit Non-Goals

This phase does not implement:

- scanner execution
- scanner changes
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

## Implementation Result

If validation passes, the accepted result is:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_IMPLEMENTATION_PASS_READY_FOR_CONTROLLED_CLI_IMPLEMENTATION_QA_GATE`
