# CID Local Media Agent — CLI Synthetic Visible Report Preflight Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.IMPLEMENTATION.V1`

## Objective

This phase implements the first minimal local preflight helper for the synthetic visible report workflow.

The implementation is intentionally isolated and development-only.

## Implementation shape selected

This phase adds an isolated helper script:

- `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`

The existing report generation CLI wrapper is not modified:

- `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`

The Markdown renderer is not modified:

- `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`

The scanner is not modified or imported:

- `scripts/cid_media_agent_scan.py`

## Development command

The development-only helper may be invoked directly as a Python script:

`python scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py --fixture tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json --output-dir <existing-dir> --format markdown`

## Allowed arguments

The preflight helper accepts only:

- `--fixture`
- `--output-dir`
- `--format markdown`
- `--allow-overwrite`

No other arguments are allowed.

## Behavior

The helper validates:

1. Required arguments are present.
2. Format is exactly `markdown`.
3. Fixture path exists.
4. Fixture basename is the approved synthetic demo fixture name.
5. Fixture can be parsed as JSON.
6. Fixture JSON is a non-empty object.
7. Renderer script exists.
8. Output directory exists.
9. Output directory is a directory.
10. Output filename remains exactly `cid_local_media_agent_synthetic_visible_report_v1.md`.
11. Existing output file blocks preflight unless `--allow-overwrite` is provided.

The helper does not generate the Markdown report.

The helper does not create output directories.

The helper does not modify input fixtures.

The helper does not import or execute the scanner.

## Output contract

Successful output includes:

- `PREFLIGHT_PASS`
- command name
- expected output filename
- synthetic/local-only notice
- human review notice

Failure output includes:

- `PREFLIGHT_FAIL`
- stable reason code
- short safe user-facing message

The helper must not print:

- absolute local paths
- raw fixture JSON
- stack traces
- environment variables
- secrets
- database strings
- network endpoints
- client media paths
- personal data

## Exit codes

The helper uses the preflight contract exit codes:

- `0`: preflight passed
- `2`: user input or contract validation failed
- `3`: safe local environment validation failed
- `4`: output safety validation failed
- `1`: unexpected controlled failure

## Explicitly blocked

This phase does not authorize:

- packaging
- installable entry point wiring
- changing the existing CLI wrapper
- changing the renderer
- changing the scanner
- scanner integration
- SaaS integration
- backend or frontend integration
- database runtime behavior
- Docker or Alembic changes
- external media probing binary execution
- real media analysis
- audio/video sync
- transcription
- translation
- subtitle generation
- NLE export
- installer behavior
- licensing behavior
- upload of client files

## Verdict

`MINIMAL_SYNTHETIC_VISIBLE_REPORT_PREFLIGHT_IMPLEMENTED_AS_DEVELOPMENT_ONLY_HELPER`

This verdict does not authorize packaging, installable entry point wiring, scanner integration, real media processing, subtitle generation, NLE export, SaaS integration, installer, licensing, or client media upload.
