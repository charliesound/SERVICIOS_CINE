# CID Local Media Agent - Own Real Material Dry Run Implementation Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.IMPLEMENTATION.GATE.V1`

## Starting HEAD

`71384472d0b04343650635d917c522f8f7105f78`

## Starting state

`OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_CLOSED_REMOTE_VERIFIED`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.READINESS.GATE.V1`

## Target next state

`OWN_REAL_MATERIAL_DRY_RUN_IMPLEMENTATION_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_QA_GATE`

## Scope

This phase implements an isolated dry-run intake planner for operator-controlled real material.

This phase does not use real media during tests.

This phase uses only synthetic fixtures in `tmp_path`.

This phase does not use client material.

This phase does not connect the real client flow.

This phase does not open video or audio files.

This phase does not read media bytes.

This phase does not execute ffmpeg, ffprobe, subprocess, or shell.

This phase does not delete, move, rename, or overwrite files.

This phase does not create outputs on real material.

This phase does not touch scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.

Directories and subfolders remain blocked until an explicit future phase.

Use of operator-controlled real material is reserved for an explicit future controlled execution phase.

Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.

## Implemented module

`scripts/local_media_agent/own_real_material_dry_run_intake.py`

Exposes `plan_own_real_material_dry_run_intake(input_path, operator_consent, read_only, allow_real_material)`.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_own_real_material_dry_run_readiness_gate_v1.py`

## Explicitly excluded historical tests

The historical renderer implementation readiness test must not be executed as a post-implementation regression:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

## Required validations

- This own real material dry run implementation gate test.
- The own real material dry run readiness gate test.
- The real media safe intake readiness gate test.
- The controlled smoke QA gate test.
- The controlled smoke implementation gate test.
- The controlled smoke readiness gate test.
- The CLI integration QA gate test.
- The CLI integration implementation gate test.
- The controlled export integration QA gate test.
- The controlled export integration implementation gate test.
- The controlled export integration readiness gate test.
- The renderer QA gate test.
- The renderer implementation gate test.
- The WSL repo guard script.
- The database regression guard script.
- Final scope check confirming only the 3 new files changed.
