# CID Local Media Agent — Second Controlled Scenario Product Classification Human Decision Record Template v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.HUMAN.DECISION.RECORD.TEMPLATE.V1

Objective: create the formal template for a future human/product decision record about non-media extension classification.
This phase does not make the product decision.
This phase does not select ignored, rejected, separate-category, configurable-policy, or any other final product behavior.

Upstream commit: 6f69cdc9524d32ed7695eb915acb980bb6cc6138
Upstream tag: cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-second-controlled-scenario-product-classification-human-decision-readiness-gate-v1-20260619
Upstream phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.HUMAN.DECISION.READINESS.GATE.V1

Template status: HUMAN_DECISION_RECORD_TEMPLATE_READY_WITH_NO_PRODUCT_OPTION_SELECTED
Upstream status still active: PRODUCT_CLASSIFICATION_DECISION_REQUIRED
Upstream readiness still active: HUMAN_DECISION_READINESS_GATE_PASS_WITH_PRODUCT_DECISION_REQUIRED

Required upstream artifacts:
docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate_v1.md
tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate.py
docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate_v1.md
tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate.py

Preserved evidence:
controlled_execution_status=PREFLIGHT_PASS
cli_exit_code=0
leak_check_exit_code=0
media_file_count=2
accepted_extension_counts=.mov:1,.wav:1
ignored_extension_counts={}
rejected_extension_counts=.exe:1,.txt:1
maximum_detected_scan_depth=3
total_selected_media_size_bucket=LE_100MB

Preserved observation:
.mov and .wav were accepted as media.
.txt and .exe were classified as rejected.
.txt and .exe were not classified as ignored.
ignored_extension_counts remained empty.
The observation is not a privacy failure.
The observation is not a sanitization failure.
The observation is not a leak-check failure.
The observation is not an execution boundary failure.
The observation concerns product classification semantics.

Human decision record fields:
decision_record_status=TO_BE_FILLED_BY_HUMAN
decision_owner=TO_BE_FILLED_BY_HUMAN
decision_date=TO_BE_FILLED_BY_HUMAN
selected_product_semantics=TO_BE_FILLED_BY_HUMAN
decision_scope=TO_BE_FILLED_BY_HUMAN
user_visible_behavior=TO_BE_FILLED_BY_HUMAN
report_visible_behavior=TO_BE_FILLED_BY_HUMAN
log_visible_behavior=TO_BE_FILLED_BY_HUMAN
runtime_change_required=TO_BE_FILLED_BY_HUMAN
qa_gate_required_before_runtime_change=TO_BE_FILLED_BY_HUMAN
client_facing_claims_allowed=TO_BE_FILLED_BY_HUMAN
migration_or_compatibility_notes=TO_BE_FILLED_BY_HUMAN
decision_rationale=TO_BE_FILLED_BY_HUMAN
evidence_reference=TO_BE_FILLED_BY_HUMAN
known_limitations=TO_BE_FILLED_BY_HUMAN

Allowed future selected_product_semantics values:
NON_MEDIA_REJECTED
NON_MEDIA_IGNORED
NON_MEDIA_SEPARATE_CATEGORY
NON_MEDIA_POLICY_CONFIGURABLE
OTHER_NAMED_PRODUCT_BEHAVIOR
This template does not choose any of these values.

Required decision questions:
Does the decision apply only to the second controlled scenario?
Does the decision apply to the general Local Media Agent scanner product?
Should .txt and .exe use the same classification behavior?
Should harmless non-media files and risky executable files share the same category?
Should rejected files be user-visible?
Should ignored files be user-visible?
Should separately classified files appear in reports?
Should policy configuration be exposed to users or remain internal?
Does the decision require runtime implementation?
Does the decision require a separate QA gate before implementation?

Required constraints for a future filled decision record:
Distinguish observed evidence from product intent.
Preserve the fact that .txt and .exe were rejected in controlled scenario evidence.
Avoid claiming that observed behavior is already final product behavior.
State whether behavior is user-visible, report-visible, log-only, or internal-only.
State whether runtime implementation is required.
State whether client-facing claims are allowed.
Preserve privacy, sanitization, leak-check, and boundary conclusions.

Explicit non-decision:
This template does not decide that .txt should be ignored.
This template does not decide that .txt should be rejected.
This template does not decide that .exe should be ignored.
This template does not decide that .exe should be rejected.
This template does not decide that rejected is preferred.
This template does not decide that ignored is preferred.
This template does not decide that separate-category is preferred.
This template does not decide that policy configuration is preferred.
This template does not allow client-facing claims.
This template does not allow runtime implementation.

Downstream blocking rule:
No downstream phase may claim clean classification pass.
No downstream phase may claim final ignored behavior.
No downstream phase may claim final rejected behavior.
No downstream phase may claim final separate-category behavior.
No downstream phase may claim final configurable-policy behavior.
No downstream phase may make client-facing claims about extension classification.
No downstream phase may change scanner behavior.
No downstream phase may change runtime behavior.
No downstream phase may change report behavior.
No downstream phase may change CLI behavior.

Out of scope:
Filling the human decision record.
Selecting final product semantics.
Runtime code changes.
Scanner behavior changes.
CLI behavior changes.
Report behavior changes.
FFmpeg or ffprobe execution.
Media probing or decoding.
Real client media.
Personal data processing.
Report generation.
Transcription.
Translation.
Subtitle generation.
Synchronization.
DaVinci Resolve, Avid, NLE, export, or upload workflows.
SaaS application changes.
Database changes.
Docker changes.
Alembic changes.
Stripe, AI Jobs, credits, or ledger changes.

Completion criteria: staged diff contains only this template document and its unit test, and repository guards pass.
