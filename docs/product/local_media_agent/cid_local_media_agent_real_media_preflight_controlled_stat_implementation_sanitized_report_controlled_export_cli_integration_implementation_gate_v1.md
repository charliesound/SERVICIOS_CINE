# CID Local Media Agent - Controlled Stat Sanitized Report Controlled Export CLI Integration Implementation Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.IMPLEMENTATION.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_GATE_V1_CLOSED`

## Starting HEAD

`09501313578aa4c271fecddf2ecc167758c6475e`

## Starting state

`CONTROLLED_EXPORT_CLI_INTEGRATION_READINESS_GATE_CLOSED_REMOTE_VERIFIED`

## Target next state

`CONTROLLED_EXPORT_CLI_INTEGRATION_IMPLEMENTED_READY_FOR_QA_GATE`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.READINESS.GATE.V1`

## Scope

This phase implements only a new, isolated, and controlled CLI.

This phase does not modify existing historical CLIs.

This phase does not connect the real client flow.

This phase does not modify the exporter.

This phase does not modify the renderer.

This phase does not modify scanner runtime.

## Implemented artifacts

- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.md`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py`
- `tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.py`

## CLI contract

The CLI calls the existing exporter `export_controlled_sanitized_markdown_report(markdown_text, output_path, export_opt_in)`.

The CLI does not duplicate write logic.

The CLI requires explicit opt-in through `--export-opt-in`.

The CLI receives already-rendered sanitized Markdown through the explicit `--markdown-text` argument.

The CLI receives the output path through the explicit `--output-path` argument.

The CLI validates output path and content through the existing exporter.

The CLI returns structured and deterministic JSON output.

The CLI returns exit code `0` on controlled success.

The CLI returns a non-zero exit code on controlled error.

The operator token must remain redacted as `REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN`.

Any test write must be limited to `tmp_path`.

## Implemented CLI API

- `run_controlled_sanitized_report_export_cli(argv)`
- `main(argv)`

## Safety boundaries

The CLI does not read Markdown from a file in this phase.

The CLI does not use real media.

The CLI does not open video or audio files.

The CLI does not execute FFmpeg.

The CLI does not execute ffprobe.

The CLI does not execute external processes.

The CLI does not use subprocess.

The CLI does not touch scanner runtime.

The CLI does not touch backend SaaS.

The CLI does not touch frontend.

The CLI does not touch DB.

The CLI does not touch Docker.

The CLI does not touch Alembic.

The CLI does not touch Stripe.

The CLI does not touch AI Jobs.

The CLI does not touch credits.

The CLI does not touch ledger.

## Historical CLI boundary

Historical Local Media Agent CLIs may exist in the repository.

This phase does not import historical CLIs.

This phase does not modify historical CLIs.

This phase does not connect the new isolated CLI to a real client flow.

## Required validation before closure

- The new CLI module compile check.
- This CLI integration implementation gate test compile check.
- This CLI integration implementation gate test.
- The controlled export integration QA gate test.
- The controlled export integration implementation gate test.
- The controlled export integration readiness gate test.
- The sanitized report renderer QA gate test.
- The sanitized report renderer implementation gate test.
- The WSL repo guard script.
- The database regression guard script.
- A final scope check confirming that only this implementation gate document, new CLI, and test changed.

## Explicitly excluded validation

The historical renderer implementation readiness test must not be executed in this implementation gate:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

That readiness test validated the pre-implementation state and asserted that no CLI specific to the controlled exporter existed yet. After this implementation gate, the new isolated CLI exists by design and is connected to `export_controlled_sanitized_markdown_report(markdown_text, output_path, export_opt_in)`, so that pre-implementation assertion must not be executed as an applicable post-implementation regression.

## Closure

`LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_GATE_V1_CLOSED`

## Closing state

`CONTROLLED_EXPORT_CLI_INTEGRATION_IMPLEMENTED_READY_FOR_QA_GATE`
