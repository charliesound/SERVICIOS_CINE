# CID Local Media Agent — CLI Synthetic Visible Report Preflight CLI Integration Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.READINESS.GATE.V1`

## Objective

This phase decides whether the preflight CLI integration contract is sufficient to authorize a future minimal implementation of a development-only `--preflight` mode in the existing synthetic visible report CLI wrapper.

This is a documentation and test-only readiness gate.

It does not modify the current CLI wrapper, the preflight helper, the renderer, the scanner, packaging, installable command wiring, or any SaaS/runtime integration.

## Inputs reviewed

This gate reviews the current contract and previously validated components:

- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_qa_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md`
- `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`
- `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`
- `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`
- `scripts/cid_media_agent_scan.py`

## Current state

The current wrapper remains a development-only synthetic visible report generator.

The current preflight helper remains a separate development-only helper.

The current wrapper does not yet expose `--preflight`.

The current helper already supports safe `PREFLIGHT_PASS` and `PREFLIGHT_FAIL` behavior for synthetic fixture/output readiness.

## Readiness decision

`READY_FOR_MINIMAL_SYNTHETIC_VISIBLE_REPORT_PREFLIGHT_CLI_INTEGRATION_WITH_RESTRICTIONS`

This gate authorizes a future implementation phase to integrate the existing preflight helper into the existing development CLI wrapper with strict restrictions.

## Future implementation allowed scope

A future implementation may:

1. Modify only the existing development wrapper:
   - `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`
2. Add implementation documentation for the integration.
3. Add implementation tests for the integration.
4. Add a development-only `--preflight` mode.
5. Delegate preflight behavior to the existing helper:
   - `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`
6. Preserve current report generation behavior when `--preflight` is absent.
7. Preserve current output filename:
   - `cid_local_media_agent_synthetic_visible_report_v1.md`

## Future implementation required behavior

The future integrated mode must prove:

1. `synthetic-visible-report --preflight` runs preflight only.
2. Success emits `PREFLIGHT_PASS`.
3. Controlled failure emits `PREFLIGHT_FAIL`.
4. Exit codes remain deterministic and aligned with the preflight contract.
5. Preflight mode does not generate the Markdown report.
6. Preflight mode does not create output directories.
7. Preflight mode does not mutate fixture files.
8. Preflight mode does not import or execute the scanner.
9. Generation mode remains unchanged when `--preflight` is absent.
10. Existing generation arguments remain supported:
    - `--fixture`
    - `--output-dir`
    - `--format markdown`
    - `--allow-overwrite`
11. Unsupported real-media-like options remain rejected.
12. Error output remains safe and controlled.

## Future output safety requirements

The future integrated preflight mode must not print:

- absolute local paths
- raw fixture JSON
- stack traces
- environment variables
- secrets
- database strings
- network endpoint details
- client media paths
- personal data

## Still explicitly blocked

This readiness gate does not authorize:

- packaging
- installable entry point wiring
- command registration
- changes to the preflight helper
- changes to the renderer
- changes to the scanner
- scanner integration
- SaaS integration
- backend integration
- frontend integration
- database runtime behavior
- Docker changes
- Alembic changes
- external media probing binary execution
- real media analysis
- audio/video sync
- transcription
- translation
- subtitle generation
- NLE export
- installer behavior
- licensing behavior
- client media upload

## Next allowed phase

The next allowed phase is:

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.IMPLEMENTATION.V1`

That future phase must remain minimal and must not open packaging, installable entry point wiring, scanner integration, SaaS integration, or real media processing.
