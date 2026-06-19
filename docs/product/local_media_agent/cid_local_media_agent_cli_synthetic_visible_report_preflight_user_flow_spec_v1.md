# CID Local Media Agent - Synthetic Visible Report Preflight User Flow Spec v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.V1`

## Purpose

Specify the controlled development user flow for `synthetic-visible-report --preflight` followed by explicit report generation, using only the already implemented wrapper CLI, the approved synthetic fixture and a local existing output directory.

This phase is documentation/test-only.

## Stable baseline

- Stable HEAD before this phase: `0ed4c8e`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.READINESS.GATE.V1`.
- Current wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Scanner remains out of scope: `scripts/cid_media_agent_scan.py`.

## Current command boundary

```bash
synthetic-visible-report --preflight --fixture <fixture-json> --output-dir <existing-dir> --format markdown [--allow-overwrite]
```

This specification does not create an installable command. It only describes the intended controlled user flow around the existing development wrapper.

## Controlled user flow

1. User chooses an approved synthetic fixture.
2. User chooses an existing local output directory.
3. User runs preflight before generation.
4. System returns `PREFLIGHT_PASS` or controlled `PREFLIGHT_FAIL`.
5. User generates only after `PREFLIGHT_PASS`.
6. Human review remains mandatory for every generated report.

## Required conditions

- fixture exists;
- fixture is synthetic;
- fixture is not real client media;
- fixture is not scanner output from real material;
- output directory exists before preflight;
- preflight must not create the output directory;
- preflight must not generate `cid_local_media_agent_synthetic_visible_report_v1.md`;
- generation remains a separate explicit command.

## Generation command after pass

```bash
synthetic-visible-report --fixture <fixture-json> --output-dir <existing-dir> --format markdown
```

## Controlled failure handling

- missing fixture returns controlled `PREFLIGHT_FAIL`;
- missing output directory returns controlled `PREFLIGHT_FAIL`;
- existing output report without overwrite returns controlled `PREFLIGHT_FAIL`;
- helper failure returns controlled `PREFLIGHT_FAIL`;
- no Python traceback is expected in normal controlled failures;
- no raw JSON dump, secret, real media path or client material should be intentionally exposed.

## User-facing rule

```text
Run preflight first. Generate only after PREFLIGHT_PASS. Review output manually.
```

## Explicitly blocked scope

This spec does not authorize:

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

## Acceptance criteria

- the spec declares this phase and stable baseline;
- the spec references the previous readiness gate;
- the spec defines preflight before generation;
- the spec requires an approved synthetic fixture;
- the spec requires an existing local output directory;
- preflight does not generate the Markdown report;
- generation remains a separate explicit command;
- controlled failure outcomes remain safe;
- renderer, scanner and helper boundaries remain intact;
- blocked scope remains explicitly closed.

## Decision

`USER_FLOW_SPEC_READY_FOR_QA_GATE_WITH_RESTRICTIONS`

A future phase may add a QA gate for this user-flow specification. Runtime packaging, installable command work, scanner integration and real media processing remain blocked until explicitly opened.
