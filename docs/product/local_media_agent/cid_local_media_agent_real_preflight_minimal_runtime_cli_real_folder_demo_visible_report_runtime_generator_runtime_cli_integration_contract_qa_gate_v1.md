# CID Local Media Agent - Visible Report Runtime Generator Runtime CLI Integration Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.QA.GATE.V1`

## Objective

Validate that the runtime CLI integration contract for the visible report generator blocks scope creep before any CLI implementation phase.

This QA gate is docs/test-only.

This QA gate does not implement a CLI command.

This QA gate does not modify the existing runtime generator.

This QA gate does not execute the scanner.

This QA gate does not use real client media.

This QA gate does not execute ffprobe or ffmpeg.

This QA gate does not perform network calls, SaaS upload, or database writes.

This QA gate does not generate synchronization, transcription, subtitles, translations, or timeline exports.

## Source Phase

Source contract phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.V1`

Source contract result:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE`

Source stable HEAD:

`df5cb486638cd3511db4020d37470bfb65df3ba8`

Source tag:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-contract-v1-20260620`

## Files Under QA

This QA gate validates:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_runtime_cli_integration_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_runtime_cli_integration_contract.py`
- `scripts/local_media_agent/visible_report_runtime_generator.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_runtime_implementation_qa_gate.py`

## QA Gate Decision

The contract is accepted only if it proves that the future CLI will remain an explicit, local-only wrapper around the already implemented renderer.

The future CLI must accept only a controlled scanner result JSON file and an authorized output root.

The future CLI must delegate rendering to:

`generate_visible_report(scanner_result, output_root)`

The future CLI must not introduce scanner execution, media probing, network access, SaaS upload, database writes, or generated post-production deliverables.

## QA Check 1 - Contract Exists And Is Traceable

The source contract document must exist.

The source contract test must exist.

The contract must reference the source HEAD, source tag, source phase, and source result.

## QA Check 2 - Future CLI Is Still Not Implemented

The following future files must not exist in this QA gate phase:

- `scripts/local_media_agent/visible_report_runtime_cli.py`
- `tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py`

If either file exists during this phase, the QA gate fails.

## QA Check 3 - Existing Renderer Interface Remains Narrow

The future CLI contract must preserve the renderer interface:

`generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path`

The future CLI contract must require delegation to:

`generate_visible_report(scanner_result, output_root)`

The CLI contract must not authorize a wider runtime interface.

## QA Check 4 - CLI Command Shape Is Explicit

The contract must require this conceptual command shape:

`python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>`

The contract must require explicit arguments.

The contract must forbid implicit current working directory input discovery.

The contract must forbid URL input, SaaS identifiers, environment secrets, and remote fetch behavior.

## QA Check 5 - CLI Arguments Are Bounded

The contract must require:

- `--scanner-result-json`
- `--output-root`

The contract may allow:

- `--dry-run`
- `--strict`
- `--print-output-path`

The contract must forbid:

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

## QA Check 6 - Input Contract Is Controlled JSON Only

The contract must require the future CLI to accept only an already-created controlled scanner result JSON file.

The contract must require local JSON parsing.

The contract must reject mutation, inference, silent correction, warning hiding, and conversion of roadmap modules into generated deliverables.

## QA Check 7 - Output Contract Is One Visible Report Only

The contract must limit output to:

- `05_reports/cid_local_media_agent_visible_report_v1.md`

The contract must forbid creation or modification of:

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

## QA Check 8 - Validation Order Is Locked

The contract must declare this future CLI validation order:

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

## QA Check 9 - Failure Contract Is Fail-Closed

The contract must require failure for:

- missing required arguments
- unsupported flags
- unsafe input path
- unsafe output path
- missing JSON
- invalid JSON
- non-object JSON root
- runtime generator validation failure
- unauthorized output path

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

## QA Check 10 - Privacy And Determinism Are Preserved

The contract must preserve the runtime privacy boundary.

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

The future CLI must remain deterministic for the same controlled JSON input and output root.

The CLI must not inject wall-clock timestamps, machine identifiers, local absolute paths into report content, or environment-dependent ordering.

## QA Check 11 - Explicit Non-Goals Block Product Overclaiming

The contract must not authorize:

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

## QA Check 12 - Validation Evidence Required

The QA gate is accepted only with:

- runtime CLI integration contract test passing
- runtime generator test passing
- controlled runtime implementation QA gate test passing
- implementation readiness tests passing
- runtime generator contract tests passing
- Python compile passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing

## QA Gate Result

If all QA checks pass, the accepted result is:

`LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS`
