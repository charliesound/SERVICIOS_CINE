# CID Local Media Agent - Synthetic Visible Report Preflight User Flow Spec QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.QA.GATE.V1`

## Purpose

Audit the completed controlled user-flow specification for `synthetic-visible-report --preflight` before any future packaging-readiness, installable entry point, scanner integration or real media workflow phase.

This phase is documentation/test-only.

## Stable baseline

- Stable HEAD before this phase: `b8bda0b`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.V1`.
- Target specification: `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_v1.md`.
- Target specification test: `tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec.py`.
- Current wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Scanner remains out of scope: `scripts/cid_media_agent_scan.py`.

## QA gate scope

Allowed files for this phase:

- `docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_qa_gate.py`

Runtime files may be audited by tests but must not be modified.

## Required QA assertions

This QA gate must confirm that the user-flow specification:

- declares the correct phase and stable baseline;
- references the previous readiness gate;
- defines preflight before generation;
- requires an approved synthetic fixture;
- requires an existing local output directory;
- states that preflight must not create the output directory;
- states that preflight must not generate `cid_local_media_agent_synthetic_visible_report_v1.md`;
- keeps generation as a separate explicit command;
- preserves controlled `PREFLIGHT_PASS` and `PREFLIGHT_FAIL` behavior;
- keeps human review mandatory;
- keeps renderer, scanner and helper boundaries intact;
- keeps all packaging, scanner integration, SaaS and real media work blocked.

## Required live behavior assertions

The QA gate may execute the existing development wrapper to confirm:

- preflight pass does not generate the Markdown report;
- generation after preflight pass is still an explicit separate step;
- missing output directory fails without creating the directory;
- existing output report without overwrite fails without modifying the report;
- controlled failures do not expose Python tracebacks.

## Explicitly blocked scope

This QA gate does not authorize:

- packaging;
- installable entry point;
- shell launcher;
- desktop app;
- installer;
- licensing;
- scanner integration;
- ffprobe/ffmpeg execution;
- real media analysis;
- sync;
- transcription;
- translation;
- subtitle generation;
- NLE/export;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work;
- upload or processing of client material.

## QA decision

`USER_FLOW_SPEC_QA_GATE_READY_FOR_NEXT_READINESS_PHASE_WITH_RESTRICTIONS`

A future phase may prepare another readiness gate, but runtime packaging, installable command work, scanner integration and real media processing remain blocked until explicitly opened.
