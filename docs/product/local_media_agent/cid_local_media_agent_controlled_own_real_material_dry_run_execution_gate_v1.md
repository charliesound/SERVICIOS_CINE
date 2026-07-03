# CID Local Media Agent - Controlled Own Real Material Dry Run Execution Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.GATE.V1`

## Starting HEAD

`c6c0e95b4c335acf0958bb15731de900786824af`

## Starting state

`OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_READINESS_GATE_CLOSED_REMOTE_VERIFIED`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.READINESS.GATE.V1`

## Target next state

`CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_RESULTS_REVIEW_GATE`

## Scope

This phase is documental/test-only.

This phase defines the controlled manual execution protocol, but does not execute real material.

This phase does not use client material.

This phase does not connect the real client flow.

No new runtime scripts are created.

The planner `own_real_material_dry_run_intake.py` is not modified.

## Controlled manual execution protocol

The future manual execution must use the audited planner directly: `plan_own_real_material_dry_run_intake`.

The future manual execution is allowed only with own/controlled material.

The future manual execution requires a single explicit local Linux file, not a folder.

The future manual execution does not allow folders.

The future manual execution does not allow Windows paths.

The future manual execution does not allow `/mnt` paths.

The future manual execution does not allow UNC paths.

The future manual execution does not allow `wsl.localhost` paths.

The future manual execution requires `operator_consent=True`.

The future manual execution requires `read_only=True`.

The future manual execution requires `allow_real_material=True`.

The real path must be supplied outside Git as `CID_OPERATOR_REAL_MATERIAL_INPUT_PATH`.

The real path must never be written to versioned files.

The real path must be documented only in a local operational note outside the repo.

Any registrable result in the repo, if any in a future phase, must be sanitized.

The sanitized result must not contain the full absolute path.

The sanitized result must not contain the real filename as the final label.

The allowed label is: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.

The future execution stops if the planner returns a rejection.

The planner does not open video or audio files.

The planner does not read media bytes.

The planner does not execute ffmpeg, ffprobe, subprocess, or shell.

The planner does not delete, move, rename, overwrite, or create outputs on real material.

Nothing is uploaded to the internet.

Scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, and ledger are not touched.

Use of real folders/subfolders requires an explicit future phase.

Use of ffprobe/ffmpeg requires an explicit future phase.

Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.

The risk of a future manual execution with own real material is low and bounded because only superficial path validation is performed, not content reading.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.py`
- `docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.py`
- `docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.py`
- `scripts/local_media_agent/own_real_material_dry_run_intake.py`

## Explicitly excluded historical tests

The historical renderer implementation readiness test must not be executed as a post-implementation regression:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py`

The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:

`tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py`

## Required validations

- This controlled own real material dry run execution gate test.
- The own real material dry run execution readiness gate test.
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
