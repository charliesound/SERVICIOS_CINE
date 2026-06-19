# CID Local Media Agent — Synthetic Visible Report Preflight User Flow Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.READINESS.GATE.V1`

## Purpose

Define a controlled user-flow readiness boundary for the already implemented `synthetic-visible-report --preflight` mode before any future packaging, installable entry point, scanner integration or real user workflow work.

## Current stable baseline

- Stable HEAD before this phase: `bf09fa8`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.QA.GATE.V1`.
- Current wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Scanner remains out of scope: `scripts/cid_media_agent_scan.py`.

## Current available command

```bash
synthetic-visible-report --preflight --fixture <fixture-json> --output-dir <existing-dir> --format markdown [--allow-overwrite]
```

This command is still a development CLI invocation, not an installable product command.

## Readiness question

This gate answers only this question:

> Is the implemented preflight behavior sufficiently defined and audited to prepare a future user-flow readiness or packaging-readiness phase without opening packaging now?

## Controlled user-flow definition

A future controlled user flow may be allowed to describe, but not yet implement, the following sequence:

1. User selects or receives an approved synthetic fixture.
2. User selects an existing local output directory.
3. User runs preflight before report generation.
4. System returns `PREFLIGHT_PASS` or safe `PREFLIGHT_FAIL`.
5. User may only proceed to generation after a pass.
6. Human review remains mandatory for all generated outputs.

## Required readiness assertions

This gate requires that:

- the wrapper already exposes `--preflight`;
- the helper remains isolated;
- preflight does not create directories;
- preflight does not generate the Markdown report;
- preflight preserves helper exit codes;
- fallback failure remains controlled;
- generation without `--preflight` remains available;
- renderer remains free of preflight logic;
- scanner remains free of preflight logic;
- no real media path, raw JSON, secret, stack trace or client material is intentionally exposed.

## Explicitly blocked scope

This readiness gate does not authorize:

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

## Decision

`READY_FOR_CONTROLLED_PREFLIGHT_USER_FLOW_SPEC_WITH_RESTRICTIONS`

A future phase may define a user-flow specification or packaging-readiness gate, but runtime packaging and installable entry point work remain blocked until explicitly opened.
