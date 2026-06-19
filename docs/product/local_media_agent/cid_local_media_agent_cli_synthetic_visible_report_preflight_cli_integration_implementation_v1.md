# CID Local Media Agent — Synthetic Visible Report Preflight CLI Integration Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.IMPLEMENTATION.V1`

## Objective

Implement the minimal controlled `--preflight` mode in the development-only `synthetic-visible-report` wrapper CLI.

The integration delegates validation to the existing isolated helper:

`scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`

## Runtime file changed

`scripts/cid_local_media_agent_synthetic_visible_report_cli.py`

## Files intentionally not changed

- `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`
- `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`
- `scripts/cid_media_agent_scan.py`
- packaging files
- SaaS backend/frontend files
- database, Docker, Alembic, Stripe, AI Jobs, credits or ledger files

## Implemented behavior

The wrapper now accepts:

```bash
synthetic-visible-report --preflight --fixture <fixture-json> --output-dir <existing-dir> --format markdown [--allow-overwrite]
```

When `--preflight` is present, the wrapper removes the wrapper-only flag, loads the existing helper by file path, delegates to `preflight.main(...)`, returns the helper exit code, does not invoke the renderer and does not generate the Markdown report.

## Preserved behavior

When `--preflight` is absent, the wrapper keeps the previous generation behavior:

```bash
synthetic-visible-report --fixture <fixture-json> --output-dir <dir> --format markdown [--allow-overwrite]
```

The expected generated filename remains `cid_local_media_agent_synthetic_visible_report_v1.md`.

## Safety constraints

This implementation remains synthetic/local-only and development-only.

It does not add packaging, installable entry point, scanner integration, ffprobe/ffmpeg execution, real media analysis, sync, transcription, translation, subtitles, NLE export, SaaS integration, database access, Docker, Alembic or upload of client material.

## Controlled failure behavior

If preflight delegation fails unexpectedly, the wrapper emits a safe controlled failure with `PREFLIGHT_FAIL`, `reason=UNEXPECTED_CONTROLLED_FAILURE` and `message=El preflight falló de forma controlada.`

No raw stack traces, absolute paths, raw JSON payloads, secrets or client media paths are intentionally exposed.

## Acceptance criteria

- `--preflight` delegates to the helper.
- `--preflight` does not generate the report.
- helper failure codes are propagated.
- generation without `--preflight` still works.
- help output documents the new mode.
- no scanner, renderer, preflight helper, packaging, SaaS, database, Docker or Alembic files are modified.
