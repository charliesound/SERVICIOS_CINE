# CID Local Media Agent — CLI Synthetic Visible Report Preflight CLI Integration Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.CONTRACT.V1`

## Objective

This phase defines the contract for a future development-only integration of the synthetic visible report preflight helper into the existing synthetic visible report CLI wrapper.

This is a documentation and test-only contract phase.

It does not modify the current CLI wrapper, preflight helper, renderer, scanner, packaging, or any SaaS/runtime integration.

## Current components

Current report generation wrapper:

- `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`

Current preflight helper:

- `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`

Current renderer:

- `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`

Current scanner, which remains out of scope:

- `scripts/cid_media_agent_scan.py`

## Future integration goal

A future implementation phase may integrate the preflight helper into the existing development CLI wrapper so that a user can perform a safe readiness check before generating the synthetic visible report.

The integration must remain development-only.

The integration must not create installable command wiring.

The integration must not change packaging files.

The integration must not touch scanner, SaaS, backend, frontend, database runtime, Docker, Alembic, external media probing binaries, real media, subtitles, NLE export, installer, licensing, or cloud upload behavior.

## Future allowed user-facing shape

A future implementation may add a single development-only mode to the existing wrapper:

`synthetic-visible-report --preflight --fixture <fixture-json> --output-dir <existing-dir> --format markdown [--allow-overwrite]`

The future mode may delegate to the existing isolated helper:

- `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`

The future integration must preserve existing report generation behavior when `--preflight` is absent.

The phrase `--preflight is absent` means the wrapper must continue to run the current generation path with no preflight delegation.

The preserved generation output filename remains exactly:

- `cid_local_media_agent_synthetic_visible_report_v1.md`

## Current behavior remains unchanged in this phase

In this phase:

- `--preflight` is not implemented.
- the current CLI wrapper is not modified.
- the preflight helper is not modified.
- the renderer is not modified.
- the scanner is not modified.
- packaging is not modified.
- no installable command wiring is added.

## Future integration requirements

A future CLI integration must prove:

1. `--preflight` runs preflight only.
2. preflight mode emits `PREFLIGHT_PASS` on success.
3. preflight mode emits `PREFLIGHT_FAIL` on controlled failure.
4. preflight mode returns deterministic exit codes from the preflight contract.
5. preflight mode does not generate the Markdown report.
6. preflight mode does not create output directories.
7. preflight mode does not mutate fixtures.
8. preflight mode does not leak absolute paths.
9. preflight mode does not print raw fixture JSON.
10. preflight mode does not print stack traces.
11. preflight mode does not import or execute the scanner.
12. report generation mode remains unchanged when `--preflight` is absent.
13. existing allowed generation arguments continue to work.
14. unsupported real-media-like options remain rejected.

## Future integration output contract

For future preflight mode, successful output may contain only:

- `PREFLIGHT_PASS`
- command name
- expected output filename
- synthetic/local-only notice
- human review notice

For future preflight mode, failure output may contain only:

- `PREFLIGHT_FAIL`
- stable reason code
- short safe user-facing message

The future integrated mode must not print:

- absolute local paths
- raw fixture JSON
- stack traces
- environment variables
- secrets
- database strings
- network endpoint details
- client media paths
- personal data

## Explicitly blocked

This contract does not authorize:

- implementing the integration
- changing the current CLI wrapper
- changing the preflight helper
- changing the renderer
- changing the scanner
- packaging
- installable command wiring
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

## Required next step before implementation

Before implementation, a readiness gate must decide whether this contract is sufficient to authorize a minimal integration.

Recommended next phase:

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.READINESS.GATE.V1`

## Verdict

`PREFLIGHT_CLI_INTEGRATION_CONTRACT_DEFINED_FOR_FUTURE_DEVELOPMENT_ONLY_MODE`

No runtime integration is authorized by this contract.
