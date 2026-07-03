# CID Local Media Agent - Own Real Material Dry Run QA Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.QA.GATE.V1`

## Starting HEAD

`03fb9180ae2a13060022aaecd355180906631d89`

## Starting state

`OWN_REAL_MATERIAL_DRY_RUN_IMPLEMENTATION_GATE_CLOSED_REMOTE_VERIFIED`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.IMPLEMENTATION.GATE.V1`

## Target next state

`OWN_REAL_MATERIAL_DRY_RUN_QA_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_READINESS_GATE`

## Scope

This phase is documental/test-only.

This phase audits the already implemented module.

This phase does not implement new runtime.

This phase does not modify `own_real_material_dry_run_intake.py`.

This phase does not use real material.

This phase does not use client material.

This phase does not connect the real client flow.

## Audited module

`scripts/local_media_agent/own_real_material_dry_run_intake.py`

The audited module exposes `plan_own_real_material_dry_run_intake`.

The audited module requires `operator_consent=True`.

The audited module requires `read_only=True`.

The audited module requires `allow_real_material=True`.

The audited module rejects empty path, relative path, Windows paths, mount paths, UNC paths, `wsl.localhost` paths, symlinks, and directories.

The audited module accepts only a synthetic file in `tmp_path` during tests.

The audited module does not open video or audio files.

The audited module does not read media bytes.

The audited module does not create output files.

The audited module does not delete, move, rename, or overwrite files.

The audited module does not execute ffmpeg, ffprobe, subprocess, or shell.

The audited module does not touch scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.

The audited module returns a safe and deterministic structure.

The audited module does not return the full absolute path or the real filename as the final label.

The audited module returns the fixed label: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.

Use of own real material is reserved for an explicit future controlled execution phase.

Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.py`
- `scripts/local_media_agent/own_real_material_dry_run_intake.py`

## Explicitly excluded historical tests

The historical renderer implementation readiness test must not be executed as a post-implementation regression:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

## Required validations

- This own real material dry run QA gate test.
- The own real material dry run implementation gate test.
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
- Final scope check confirming only the 2 new files changed.
