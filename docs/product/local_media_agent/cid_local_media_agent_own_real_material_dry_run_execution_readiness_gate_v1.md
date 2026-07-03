# CID Local Media Agent - Own Real Material Dry Run Execution Readiness Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.READINESS.GATE.V1`

## Starting HEAD

`73633d5943837665eb4278425d89585b60107447`

## Starting state

`OWN_REAL_MATERIAL_DRY_RUN_QA_GATE_CLOSED_REMOTE_VERIFIED`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.QA.GATE.V1`

## Target next state

`OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_READINESS_GATE_PASSED_READY_FOR_CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_GATE`

## Scope

This phase is documental/test-only.

This phase prepares a future controlled execution, but does not execute it.

This phase does not use real material yet.

This phase does not use client material.

This phase does not connect the real client flow.

## Future controlled execution conditions

The future execution must use exclusively own/controlled material.

The future execution must use a single explicit local Linux file, not a folder.

The future execution must require `operator_consent=True`.

The future execution must require `read_only=True`.

The future execution must require `allow_real_material=True`.

The future execution must use the audited planner: `plan_own_real_material_dry_run_intake`.

The future execution must continue to not open video or audio files.

The future execution must continue to not read media bytes.

The future execution must continue to not use ffmpeg, ffprobe, subprocess, or shell.

The future execution must not delete, move, rename, overwrite, or create outputs on real material.

The future execution must not upload anything to the internet.

The future execution must not touch scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.

The future execution must return only a sanitized report.

The future execution must not return the full absolute path or the real filename as the final label.

The future execution must return the fixed label: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.

The future execution must stop if the planner returns a rejection.

The future execution must document the real path used manually outside the repo, not inside Git.

Use of real folders/subfolders requires an explicit future phase.

Use of ffprobe/ffmpeg requires an explicit future phase.

Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.py`
- `scripts/local_media_agent/own_real_material_dry_run_intake.py`

## Explicitly excluded historical tests

The historical renderer implementation readiness test must not be executed as a post-implementation regression:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

## Required validations

- This own real material dry run execution readiness gate test.
- The own real material dry run QA gate test.
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
