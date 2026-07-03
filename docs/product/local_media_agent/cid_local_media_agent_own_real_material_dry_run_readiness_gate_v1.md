# CID Local Media Agent - Own Real Material Dry Run Readiness Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.READINESS.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_V1_CLOSED`

## Starting HEAD

`af14cc8367e8a18a20881e765798020323fe4763`

## Starting state

`REAL_MEDIA_SAFE_INTAKE_READINESS_GATE_CLOSED_REMOTE_VERIFIED`

## Target next state

`OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_IMPLEMENTATION_GATE`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_SAFE_INTAKE.READINESS.GATE.V1`

## Scope

This phase is documentation-only and test-only.

This phase does not use real media yet.

This phase prepares a future test with operator-controlled real material, not client material.

Real client material remains blocked.

## Future own real material dry-run conditions

The future dry-run must be read-only.

The future dry-run must use a working copy, not unique originals.

The future dry-run must require explicit operator consent.

The future dry-run must require an explicit and controlled local Linux path.

The future dry-run must reject Windows paths, `/mnt` paths, UNC paths, and `wsl.localhost` paths.

The future dry-run must reject ambiguous or non-absolute paths.

The future dry-run must first be limited to a single file or small subfolder.

The future dry-run must not delete, move, rename, or overwrite original material.

The future dry-run must not upload material to the internet.

The future dry-run must not touch SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.

The future dry-run must emit sanitized reports.

The future dry-run must sanitize filenames, absolute paths, tokens, and sensitive metadata.

The future dry-run must not execute ffmpeg or ffprobe except by explicit future phase.

The future dry-run must not use subprocess except by explicit future phase.

The future implementation gate must remain minimal and controlled.

Use of real client material requires an explicit future `CLIENT_REAL_PILOT.READINESS.GATE` phase, not this one.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_real_media_safe_intake_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_media_safe_intake_readiness_gate_v1.py`

## Explicitly excluded historical tests

The historical renderer implementation readiness test must not be executed as a post-implementation regression:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

## Required validations

- This own real material dry run readiness gate test.
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

## Closure

`LOCAL_MEDIA_AGENT_OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_V1_CLOSED`

## Closing state

`OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_IMPLEMENTATION_GATE`
