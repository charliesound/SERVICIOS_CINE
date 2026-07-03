# CID Local Media Agent - Controlled Stat Sanitized Report Controlled Export CLI Integration Controlled Smoke Implementation Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.CONTROLLED_SMOKE.IMPLEMENTATION.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_CONTROLLED_SMOKE_IMPLEMENTATION_GATE_V1_CLOSED`

## Starting HEAD

`ffb16ae8e26aaebf6e279e5ee3af461fbcb4d083`

## Starting state

`CONTROLLED_SMOKE_READINESS_GATE_CLOSED_REMOTE_VERIFIED`

## Target next state

`CONTROLLED_SMOKE_IMPLEMENTED_READY_FOR_SMOKE_EXECUTION`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.CONTROLLED_SMOKE.READINESS.GATE.V1`

## Scope

This phase implements only a controlled smoke isolated from the CLI.

This phase does not modify the CLI.

This phase does not modify the exporter.

This phase does not modify the renderer.

This phase does not modify historical CLIs.

This phase does not connect the real client flow.

This phase uses only test sanitized Markdown, not real media.

This phase does not import renderer or implementation.

This phase does not use ffmpeg, ffprobe, subprocess, or shell.

This phase writes only to a controlled path supplied by test or operator.

The new smoke delegates validation, opt-in, sanitization, path safety, and no-overwrite to the existing CLI and exporter.

The new smoke does not duplicate write logic.

Real client material remains blocked until explicit future phases.

## New controlled smoke script

`scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli_controlled_smoke.py`

### Exposed function

`run_controlled_sanitized_report_export_cli_controlled_smoke(output_path: str, export_opt_in: bool) -> dict[str, object]`

### Requirements

The smoke must import only `run_controlled_sanitized_report_export_cli` from the existing CLI.

The smoke must use a fixed fixture Markdown containing the expected title and `REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN`.

The smoke must not import renderer (`real_media_preflight_controlled_stat_sanitized_report_renderer`).

The smoke must not import implementation (`real_media_preflight_controlled_stat_implementation`).

The smoke must not import `ControlledStatImplementationRequest`, `build_controlled_stat_implementation_result`, or `build_controlled_stat_sanitized_markdown_report`.

The smoke must capture CLI stdout via `io.StringIO` and parse emitted JSON, without subprocess or shell.

The smoke must return a deterministic dict with at least: `status`, `cli_exit_code`, `output_path`, `created`, `errors`, `verification_status`.

The smoke may expose `main()`, but must have no side effects on import.

## Safety boundaries

The smoke does not read real media.

The smoke does not scan folders.

The smoke does not execute ffmpeg, ffprobe, subprocess, or shell.

The smoke does not touch scanner runtime.

The smoke does not touch backend SaaS.

The smoke does not touch frontend.

The smoke does not touch DB.

The smoke does not touch Docker.

The smoke does not touch Alembic.

The smoke does not touch Stripe.

The smoke does not touch AI Jobs.

The smoke does not touch credits.

The smoke does not touch ledger.

No real tokens.

No real client names.

No real paths.

No Windows paths.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_readiness_gate_v1.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli_controlled_smoke.py`
- `tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_implementation_gate_v1.py`

## Explicitly excluded historical tests

The historical renderer implementation readiness test must not be executed as a post-implementation regression:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

## Required validations

- This controlled smoke implementation gate test.
- The controlled smoke readiness gate test.
- The CLI integration QA gate test.
- The CLI integration implementation gate test.
- The CLI integration readiness gate test.
- The controlled export integration QA gate test.
- The controlled export integration implementation gate test.
- The controlled export integration readiness gate test.
- The renderer QA gate test.
- The renderer implementation gate test.
- The WSL repo guard script.
- The database regression guard script.
- Final scope check confirming only the 3 new files changed.

## Closure

`LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_CONTROLLED_SMOKE_IMPLEMENTATION_GATE_V1_CLOSED`

## Closing state

`CONTROLLED_SMOKE_IMPLEMENTED_READY_FOR_SMOKE_EXECUTION`
