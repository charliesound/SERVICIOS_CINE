# CID Local Media Agent - Controlled Own Real Material Dry Run Sanitized Results Review Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.SANITIZED_RESULTS_REVIEW.GATE.V1`

## Starting HEAD

`9d9d4573533e87ac635512517755c64fd62804e4`

## Starting state

`CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_RESULTS_REVIEW_READINESS_GATE_CLOSED_REMOTE_VERIFIED`

## Previous closed phase

`CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.RESULTS_REVIEW.READINESS.GATE.V1`

## Target next state

`CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_SANITIZED_RESULTS_REVIEW_GATE_PASSED_READY_FOR_MANUAL_EXECUTION_RECORD_GATE`

## Scope

This phase is documental/test-only.

This phase reviews only synthetic sanitized fixtures.

This phase does not review real results.

This phase does not execute the planner.

This phase does not use real material.

This phase does not use client material.

This phase does not ask for or store real paths.

This phase does not read external operational logs.

This phase does not create new runtime scripts.

## Sanitized result review contract

The review accepts only a sanitized dict structure.

The accepted structure must contain:

- `status`
- `accepted`
- `sanitized_input_label`
- `errors`
- `warnings`
- `real_material_scope`
- `read_only`
- `operator_consent`
- `next_required_gate`

The only allowed label for input is: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.

A valid accepted result must contain:

- `accepted=True`
- `read_only=True`
- `operator_consent=True`
- `real_material_scope=OWN_CONTROLLED_ONLY`
- `sanitized_input_label=SANITIZED_OWN_REAL_MATERIAL_INPUT`
- `errors=[]`

A valid rejected result must preserve:

- `accepted=False`
- `status` indicating rejection
- `errors` non-empty or equivalent sanitized reason
- `sanitized_input_label=SANITIZED_OWN_REAL_MATERIAL_INPUT`

A planner rejection must never be converted to acceptance during review.

The review must reject or mark as not suitable any result containing:

- a real absolute path
- a real filename
- Windows paths
- mount paths
- UNC paths
- wsl localhost paths
- unsanitized keys such as `input_path`, `absolute_path`, `file_name`, `filename`, `source_path`, `real_path`

The review must not infer video/audio metadata.

The review must not open media.

The review must not read bytes.

The review must not execute ffmpeg, ffprobe, subprocess, or shell.

The review must not create outputs on real material.

The review must not upload anything to the internet.

Any versioned evidence must be sanitized.

Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.

The real path used by the operator, if any in a future execution, remains documented only outside the repo.

## Required audited artifacts

- `docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_results_review_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_controlled_own_real_material_dry_run_results_review_readiness_gate_v1.py`
- `docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.py`
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

- This controlled own real material dry run sanitized results review gate test.
- The controlled own real material dry run results review readiness gate test.
- The controlled own real material dry run execution gate test.
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
