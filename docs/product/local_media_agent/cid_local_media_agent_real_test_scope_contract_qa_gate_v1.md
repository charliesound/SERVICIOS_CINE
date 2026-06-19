# CID Local Media Agent - Real Test Scope Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1`

## Purpose

Audit the completed real test scope contract before any privacy safety gate, real input-folder contract, real preflight contract, real preflight implementation, scanner integration or real media execution.

This phase is documentation/test-only.

It does not execute real media, does not call ffprobe/ffmpeg on real files, does not implement real preflight, does not implement scanner integration, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `8a697c0`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.V1`.
- Target contract: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md`.
- Target contract test: `tests/unit/test_cid_local_media_agent_real_test_scope_contract.py`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## QA gate scope

Allowed files for this phase:

- `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_test_scope_contract_qa_gate.py`

Runtime files may be audited by tests but must not be modified.

## Required QA assertions

This QA gate must confirm that the real test scope contract:

- declares the correct phase and stable baseline;
- references the completed packaging readiness QA gate;
- declares documentation/test-only status;
- blocks real media execution in the current phase;
- blocks ffprobe/ffmpeg execution on real files;
- blocks scanner integration;
- blocks real report generation;
- blocks runtime implementation;
- defines the first real test as internal laboratory only;
- allows only owned or explicitly authorized material;
- requires copied test media, never original camera masters;
- excludes client material unless a later explicit client authorization gate exists;
- keeps input and output folders manually selected and local;
- sets read-only inspection as the default safety posture;
- requires human review before considering the result usable.

## Required exclusion assertions

This QA gate must confirm that the first real test scope excludes:

- client material;
- confidential productions;
- original camera masters;
- destructive operations;
- moving, deleting or renaming files;
- transcoding;
- upload;
- cloud processing;
- external API calls;
- sync;
- transcription;
- translation;
- subtitle generation;
- NLE export;
- packaging;
- installable entry point;
- shell launcher;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work.

## Required next-step assertions

This QA gate must confirm that the contract still requires additional gates before real execution:

1. `CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
6. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
7. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this QA gate

This QA gate does not authorize:

- real media execution;
- ffprobe or ffmpeg execution on real files;
- real preflight implementation;
- scanner integration;
- real report generation;
- runtime implementation;
- packaging implementation;
- installable entry point;
- shell launcher;
- client delivery;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work.

## QA decision

`REAL_TEST_SCOPE_CONTRACT_QA_GATE_READY_FOR_PRIVACY_SAFETY_GATE_WITH_RESTRICTIONS`

A future phase may define a privacy safety gate. No real media execution is authorized by this QA gate.
