# CID Local Media Agent — Second Controlled Scenario Product Classification Human Decision Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.HUMAN.DECISION.READINESS.GATE.V1`

## Objective

This readiness gate prepares the required human product decision point for non-media extension classification.

The gate exists because the upstream product classification decision gate established:

`PRODUCT_CLASSIFICATION_DECISION_REQUIRED`

This phase does not make the product decision. It only validates that the decision is ready to be made explicitly, with preserved evidence, bounded options, and clear downstream constraints.

## Upstream stable baseline

This readiness gate depends on the closed upstream decision gate:

- Commit: `55296400c2f9ae8834f9fcaa31e1df23e0b00a6a`
- Tag: `cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-second-controlled-scenario-product-classification-decision-gate-v1-20260619`
- Phase: `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.DECISION.GATE.V1`

## Required upstream artifacts

This readiness gate requires the following upstream artifacts to exist:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate.py`
- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate.py`

## Gate result

The required result for this phase is:

`HUMAN_DECISION_READINESS_GATE_PASS_WITH_PRODUCT_DECISION_REQUIRED`

This means:

- The evidence is ready for human/product review.
- The product decision is still not made.
- `PRODUCT_CLASSIFICATION_DECISION_REQUIRED` remains active.
- Runtime behavior remains unchanged.
- Client-facing claims remain blocked.
- A later human decision record or product classification contract is still required.

## Preserved evidence

The readiness gate must preserve the current evidence exactly:

- `controlled_execution_status=PREFLIGHT_PASS`
- `cli_exit_code=0`
- `leak_check_exit_code=0`
- `media_file_count=2`
- `accepted_extension_counts=.mov:1,.wav:1`
- `ignored_extension_counts={}`
- `rejected_extension_counts=.exe:1,.txt:1`
- `maximum_detected_scan_depth=3`
- `total_selected_media_size_bucket=LE_100MB`

## Preserved observation

The current observation remains active:

- `.mov` and `.wav` were accepted as media.
- `.txt` and `.exe` were classified as rejected.
- `.txt` and `.exe` were not classified as ignored.
- `ignored_extension_counts` remained empty.
- The observation is not a privacy failure.
- The observation is not a sanitization failure.
- The observation is not a leak-check failure.
- The observation is not an execution boundary failure.
- The observation concerns product classification semantics.

## Human decision options to prepare

The future human/product decision must explicitly choose one of these options, or define another named product behavior:

1. Non-media files are rejected.
2. Non-media files are ignored.
3. Non-media files are classified into a separate category.
4. Non-media classification is configurable by policy.
5. Another named product behavior is required.

This readiness gate does not select any option.

## Required human decision record fields

A future human decision record must include:

- `decision_owner`
- `decision_date`
- `selected_product_semantics`
- `decision_scope`
- `user_visible_behavior`
- `report_visible_behavior`
- `log_visible_behavior`
- `runtime_change_required`
- `qa_gate_required_before_runtime_change`
- `client_facing_claims_allowed`
- `migration_or_compatibility_notes`
- `decision_rationale`
- `evidence_reference`
- `known_limitations`

## Required decision scope questions

The future human/product decision must answer:

1. Does the decision apply only to the second controlled scenario?
2. Does the decision apply to the general Local Media Agent scanner product?
3. Should `.txt` and `.exe` use the same classification behavior?
4. Should harmless non-media files and risky executable files share the same category?
5. Should rejected files be user-visible?
6. Should ignored files be user-visible?
7. Should separately classified files appear in reports?
8. Should policy configuration be exposed to users or remain internal?
9. Does the decision require runtime implementation?
10. Does the decision require a separate QA gate before implementation?

## Downstream blocking rule

Until a later authorized human decision record or product classification contract exists:

- No downstream phase may claim clean classification pass.
- No downstream phase may claim final ignored behavior.
- No downstream phase may claim final rejected behavior.
- No downstream phase may claim final separate-category behavior.
- No downstream phase may claim final configurable-policy behavior.
- No downstream phase may make client-facing claims about extension classification.
- No downstream phase may change scanner behavior.
- No downstream phase may change runtime behavior.
- No downstream phase may change report behavior.
- No downstream phase may change CLI behavior.

## Explicit non-decision

This readiness gate explicitly does not decide:

- That `.txt` should be ignored.
- That `.txt` should be rejected.
- That `.exe` should be ignored.
- That `.exe` should be rejected.
- That `.txt` and `.exe` should share the same category.
- That `.txt` and `.exe` should use different categories.
- That rejected is the preferred product behavior.
- That ignored is the preferred product behavior.
- That separate-category is the preferred product behavior.
- That policy configuration is the preferred product behavior.

## Out-of-scope actions

This readiness gate does not authorize:

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

- This readiness gate document exists.
- The readiness gate unit test exists.
- The upstream product classification decision gate document exists.
- The upstream product classification decision gate test exists.
- The upstream observation classification QA gate document exists.
- The upstream observation classification QA gate test exists.
- The readiness gate validates `HUMAN_DECISION_READINESS_GATE_PASS_WITH_PRODUCT_DECISION_REQUIRED`.
- The readiness gate validates that `PRODUCT_CLASSIFICATION_DECISION_REQUIRED` remains active.
- The readiness gate validates that no product option is selected.
- The readiness gate validates the required human decision record fields.
- The readiness gate validates the required decision scope questions.
- The readiness gate validates that client-facing claims remain blocked.
- The readiness gate validates that runtime changes remain blocked.
- The staged diff contains only this readiness gate document and its unit test.
- Repository guards pass.
