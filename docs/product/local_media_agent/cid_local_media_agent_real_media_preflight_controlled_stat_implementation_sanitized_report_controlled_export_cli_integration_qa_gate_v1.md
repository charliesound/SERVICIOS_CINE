# CID Local Media Agent - Controlled Stat Sanitized Report Controlled Export CLI Integration QA Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.QA.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_QA_GATE_V1_CLOSED`

## Starting HEAD

`f146c4d1a4fe79d7be75e2125d7196af9d02bdc6`

## Starting state

`CONTROLLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_GATE_CLOSED_REMOTE_VERIFIED`

## Target next state

`CONTROLLED_EXPORT_CLI_INTEGRATION_QA_PASSED_READY_FOR_NEXT_EXPLICIT_GATE`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.IMPLEMENTATION.GATE.V1`

## Scope

This phase is documentation-only and test-only.

This phase does not implement new runtime.

This phase does not modify the CLI.

This phase does not modify the exporter.

This phase does not modify the renderer.

This phase does not modify historical CLIs.

This phase does not connect the real client flow.

This phase audits the already implemented isolated controlled CLI.

## Audited CLI boundaries

The audited CLI accepts `--markdown-text`.

The audited CLI accepts `--output-path`.

The audited CLI requires `--export-opt-in`.

The audited CLI calls the existing exporter `export_controlled_sanitized_markdown_report(markdown_text, output_path, export_opt_in)`.

The audited CLI does not duplicate write logic.

The audited CLI returns deterministic and safe JSON.

The audited CLI returns exit code `0` on controlled success.

The audited CLI returns a non-zero exit code on controlled error.

The audited CLI rejects non-sanitized Markdown.

The audited CLI rejects execution without opt-in.

The audited CLI validates unsafe paths through the exporter.

Any test write must be limited to `tmp_path`.

The audited CLI does not use real media.

The audited CLI does not execute FFmpeg, ffprobe, or external process execution.

The audited CLI does not touch scanner runtime, backend SaaS, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py`
- `scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py`
- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_qa_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_implementation_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_qa_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.md`

## Explicitly excluded validation

The historical renderer implementation readiness test must not be executed in this QA gate:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

That readiness test validated the pre-implementation state and asserted that no CLI specific to the controlled exporter existed yet. After the implementation gate, the new isolated CLI exists by design and is connected to `export_controlled_sanitized_markdown_report(markdown_text, output_path, export_opt_in)`, so that pre-implementation assertion must not be executed as an applicable post-implementation regression.

## Required validations

- This CLI integration QA gate test.
- The CLI integration implementation gate test.
- The controlled export integration QA gate test.
- The controlled export integration implementation gate test.
- The controlled export integration readiness gate test.
- The renderer QA gate test.
- The renderer implementation gate test.
- The WSL repo guard script.
- The database regression guard script.
- Final scope check confirming only this QA document and QA test changed.

## Closure

`LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_QA_GATE_V1_CLOSED`

## Closing state

`CONTROLLED_EXPORT_CLI_INTEGRATION_QA_PASSED_READY_FOR_NEXT_EXPLICIT_GATE`
