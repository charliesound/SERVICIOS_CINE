# CID Local Media Agent — Synthetic Visible Report Preflight CLI Integration QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.QA.GATE.V1`

## Purpose

Audit the completed minimal `--preflight` integration in the development-only `synthetic-visible-report` wrapper CLI before any future packaging, installable entry point, scanner integration or user-flow work.

## Previous completed implementation

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.IMPLEMENTATION.V1`

The wrapper now accepts:

```bash
synthetic-visible-report --preflight --fixture <fixture-json> --output-dir <existing-dir> --format markdown [--allow-overwrite]
```

and delegates validation to:

`scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`

## QA gate scope

This phase is documentation/test-only.

Allowed files:

- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_qa_gate.py`

## Runtime files audited but not modified

- `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`
- `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`
- `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`
- `scripts/cid_media_agent_scan.py`

## Required QA assertions

The QA gate must confirm:

- `--preflight` is present in the wrapper help and source.
- preflight mode delegates to the helper.
- preflight mode does not generate `cid_local_media_agent_synthetic_visible_report_v1.md`.
- helper failure exit codes are preserved.
- generation without `--preflight` remains preserved.
- fallback failure is controlled with `PREFLIGHT_FAIL` and `reason=UNEXPECTED_CONTROLLED_FAILURE`.
- renderer remains free of preflight integration.
- scanner remains free of preflight integration.
- helper remains isolated and is not modified by this QA gate.
- no raw JSON, stack traces, secrets or client media paths are intentionally exposed by the wrapper fallback.

## Explicitly blocked scope

This QA gate does not authorize:

- packaging
- installable entry point
- scanner integration
- ffprobe/ffmpeg execution
- real media analysis
- sync
- transcription
- translation
- subtitle generation
- NLE/export
- installer or licensing work
- SaaS/backend/frontend/database/Docker/Alembic work
- Stripe, AI Jobs, credits or ledger work
- upload or processing of client material

## QA decision

`QA_GATE_READY_FOR_CONTROLLED_PREFLIGHT_USER_FLOW_OR_PACKAGING_READINESS_WITH_RESTRICTIONS`

The next phase may be another documentation/test-only readiness gate. Runtime packaging, scanner integration and real media remain blocked until explicitly opened.
