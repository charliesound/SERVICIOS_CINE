# CID Local Media Agent — Second Controlled Scenario Product Classification Decision Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.DECISION.GATE.V1`

## Objective

This decision gate creates the required product decision checkpoint before any future contract can define the final behavior for non-media extension classification.

The gate exists because the second controlled scenario produced an active observation:

`QA_GATE_PASS_WITH_ACTIVE_OBSERVATION`

In that observation:

- `.mov` and `.wav` were accepted as media.
- `.txt` and `.exe` were classified as rejected.
- `.txt` and `.exe` were not classified as ignored.
- `ignored_extension_counts` remained empty.
- The result did not violate privacy, sanitization, leak-check, or execution boundary guarantees.
- Product semantics for ignored versus rejected remain undecided.

## Upstream stable baseline

This decision gate depends on the closed upstream QA gate:

- Commit: `6f30152ef7ade860a18ef45d40828718a44a3598`
- Tag: `cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-second-controlled-scenario-observation-classification-qa-gate-v1-20260619`
- Phase: `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.OBSERVATION.CLASSIFICATION.QA.GATE.V1`

## Required upstream artifacts

This decision gate requires the following upstream artifacts to exist:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate.py`
- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract.py`

## Gate status

The required status for this phase is:

`PRODUCT_CLASSIFICATION_DECISION_REQUIRED`

This means the system is not authorized to finalize extension classification semantics yet.

## Decision required

A future authorized product classification contract must explicitly decide one of the following product semantics before client-facing claims or runtime changes are allowed:

1. Non-media files are rejected.
2. Non-media files are ignored.
3. Non-media files are classified into a separate category.
4. Non-media classification is configurable by policy.
5. Non-media classification requires another named product behavior.

This decision gate does not choose any of those options.

## Preserved controlled execution facts

The existing controlled execution facts remain preserved:

- `controlled_execution_status=PREFLIGHT_PASS`
- `cli_exit_code=0`
- `leak_check_exit_code=0`
- `media_file_count=2`
- `accepted_extension_counts=.mov:1,.wav:1`
- `ignored_extension_counts={}`
- `rejected_extension_counts=.exe:1,.txt:1`
- `maximum_detected_scan_depth=3`
- `total_selected_media_size_bucket=LE_100MB`

## Required decision constraints

Any future product classification contract must preserve these constraints:

1. It must distinguish evidence from product intent.
2. It must not pretend that the current observation already defines final product behavior.
3. It must state whether `.txt`, `.exe`, and other non-media files are ignored, rejected, separately classified, or policy-configured.
4. It must state whether the behavior is user-visible, report-visible, log-only, or internal-only.
5. It must state whether the behavior applies only to this controlled scenario or to the general scanner product.
6. It must state whether migration or compatibility concerns exist for previous reports.
7. It must state whether any runtime implementation phase is required.
8. It must require a separate QA gate before runtime behavior changes.

## Downstream blocking rule

No downstream phase may claim a clean classification pass until a later authorized product classification contract resolves ignored versus rejected behavior.

No downstream phase may make client-facing claims about ignored or rejected extension behavior until that product classification contract exists.

No downstream phase may change scanner behavior, runtime behavior, reporting behavior, or CLI behavior based only on this decision gate.

## Explicit non-decision

This gate explicitly does not decide:

- That `.txt` should be ignored.
- That `.txt` should be rejected.
- That `.exe` should be ignored.
- That `.exe` should be rejected.
- That rejected is better than ignored.
- That ignored is better than rejected.
- That the observed behavior is final product behavior.
- That client-facing documentation can describe final ignored or rejected semantics.

## Out-of-scope actions

This decision gate does not authorize:

- Runtime code changes.
- Scanner behavior changes.
- CLI behavior changes.
- Report behavior changes.
- FFmpeg or ffprobe execution.
- Media probing or decoding.
- Real client media.
- Personal data processing.
- Report generation.
- Transcription.
- Translation.
- Subtitle generation.
- Synchronization.
- DaVinci Resolve, Avid, NLE, export, or upload workflows.
- SaaS application changes.
- Database changes.
- Docker changes.
- Alembic changes.
- Stripe, AI Jobs, credits, or ledger changes.

## Completion criteria

This phase is complete only when:

- This decision gate document exists.
- The decision gate unit test exists.
- The upstream observation classification QA gate document exists.
- The upstream observation classification QA gate test exists.
- The upstream observation classification contract document exists.
- The upstream observation classification contract test exists.
- The decision gate validates `PRODUCT_CLASSIFICATION_DECISION_REQUIRED`.
- The decision gate validates that no final ignored versus rejected behavior is selected.
- The decision gate validates that client-facing claims remain blocked.
- The decision gate validates that runtime changes remain blocked.
- The staged diff contains only this decision gate document and its unit test.
- Repository guards pass.
