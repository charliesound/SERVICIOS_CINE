# CID Local Media Agent - Customer Demo Production Use Path Scope Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY_SINGLE_FILE_METADATA.CUSTOMER_DEMO.PRODUCTION_USE_PATH.SCOPE.GATE.V1

CANONICAL_PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PRODUCTION_USE_PATH.SCOPE.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PRODUCTION_USE_PATH_SCOPE_GATE_V1_CLOSED

BASE_HEAD:
5614ff43c2d6e2f64b9abf95b4c4c1f950fdf8d2

BASE_COMMIT:
5614ff4 test: add CID Local Media Agent customer demo human review gate

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-human-review-gate-v1-20260701

CURRENT_STATUS:
CUSTOMER_DEMO_MEETING_PACK_HUMAN_REVIEW_ACCEPTED_WITH_RESERVATIONS

REVIEW_TARGET_DOCUMENT:
docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md

REVIEW_SOURCE_DOCUMENT:
docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_gate_v1.md

TARGET_FINAL_STATUS:
LOCAL_MEDIA_AGENT_APPROVED_FOR_CONTROLLED_PRODUCTION_USE

PURPOSE:
Define the mandatory controlled path from safe private prospect conversation to eventual production use.

This gate does not approve production use.
This gate does not approve paid delivery.
This gate does not approve private pilot execution.
This gate does not approve customer material processing.
This gate does not approve real media processing.
This gate does not create an installer.
This gate does not create binaries.
This gate does not modify implementation.
This gate does not modify the customer demo meeting pack.

WHY_THIS_GATE_EXISTS:
The current state is safe for private prospect review only.
Production use requires more than a meeting pack.
Production use requires prospect feedback, pilot scope, real-media boundaries, technical runtime maturity, privacy controls, packaging, installation, licensing, support, rollback, and operational acceptance.
This gate prevents accidental promotion from controlled demo to production product.

CURRENT_ALLOWED_USE:
Private one-to-one trusted prospect conversation.
Private producer conversation.
Private executive producer conversation.
Private postproduction supervisor conversation.
Private requirements discussion.
Private pilot-boundary discussion without customer files.
Private commercial discovery conversation.

CURRENT_FORBIDDEN_USE:
Public sales deck.
Public demo.
Website launch material.
Paid delivery proposal.
Installer delivery.
Binary distribution.
Workshop material.
Customer onboarding material.
Real project execution.
Customer file processing.
Production workflow replacement.
Private pilot execution.

PRODUCTION_USE_DEFINITION:
Production use means the product can be installed or operated for a real customer or real production environment under a written scope.
Production use means real customer material may be processed only within approved boundaries.
Production use means operational risks, privacy risks, data-handling risks, support risks, and rollback risks have been accepted.
Production use means the product has a defined support model and known limitations.
Production use does not mean unlimited processing.
Production use does not mean SaaS integration by default.
Production use does not mean all roadmap features are complete.

MANDATORY_PATH_TO_PRODUCTION:
01_PROSPECT_FEEDBACK_CAPTURE_READINESS_GATE
02_PROSPECT_FEEDBACK_CAPTURE_GATE
03_PRIVATE_PILOT_BOUNDARY_READINESS_GATE
04_PRIVATE_PILOT_BOUNDARY_GATE
05_REAL_MEDIA_PREFLIGHT_PLANNING_GATE
06_REAL_MEDIA_PREFLIGHT_READINESS_GATE
07_REAL_MEDIA_PREFLIGHT_CONTROLLED_EXECUTION_GATE
08_REAL_MEDIA_PREFLIGHT_EXECUTION_QA_GATE
09_SINGLE_FILE_REAL_METADATA_IMPLEMENTATION_SCOPE_GATE
10_SINGLE_FILE_REAL_METADATA_IMPLEMENTATION_GATE
11_SINGLE_FILE_REAL_METADATA_QA_GATE
12_LOCAL_FOLDER_READ_ONLY_SCAN_SCOPE_GATE
13_LOCAL_FOLDER_READ_ONLY_SCAN_IMPLEMENTATION_GATE
14_LOCAL_FOLDER_READ_ONLY_SCAN_QA_GATE
15_CUSTOMER_PRIVACY_AND_DATA_HANDLING_GATE
16_INSTALLATION_AND_DEPENDENCY_STRATEGY_GATE
17_LICENSE_AND_ACTIVATION_STRATEGY_GATE
18_PACKAGING_READINESS_GATE
19_PACKAGING_GATE
20_PACKAGING_QA_GATE
21_PRIVATE_BETA_OPERATIONAL_READINESS_GATE
22_PRIVATE_BETA_EXECUTION_GATE
23_PRIVATE_BETA_QA_GATE
24_PRODUCTION_USE_READINESS_GATE
25_PRODUCTION_USE_ACCEPTANCE_GATE

NON_NEGOTIABLE_PRODUCTION_BLOCKERS:
No production use without a written customer/pilot boundary.
No production use without explicit real-media approval.
No production use without privacy and data-handling rules.
No production use without installation or execution strategy.
No production use without rollback strategy.
No production use without support boundary.
No production use without known limitations.
No production use without validation on controlled real-media scenarios.
No production use without explicit acceptance gate.

PROSPECT_FEEDBACK_REQUIREMENTS:
Capture producer pain points.
Capture buyer/user/approver roles.
Capture current workflow.
Capture file volume expectations.
Capture operating systems.
Capture storage locations.
Capture security/privacy concerns.
Capture budget sensitivity.
Capture must-have features.
Capture nice-to-have features.
Capture deal blockers.
Capture private pilot interest.
Capture what the prospect would pay for.
Capture what the prospect refuses to risk.

PRIVATE_PILOT_BOUNDARY_REQUIREMENTS:
Define allowed customer.
Define allowed operator.
Define allowed machine.
Define allowed material type.
Define allowed file count.
Define allowed folder count.
Define allowed output reports.
Define forbidden operations.
Define duration.
Define support responsibility.
Define rollback plan.
Define data retention rule.
Define deletion rule.
Define confidentiality expectations.
Define success criteria.
Define stop conditions.

REAL_MEDIA_PREFLIGHT_REQUIREMENTS:
Real media must be explicitly approved before execution.
Real media must be non-confidential or separately authorized.
Real media path must be explicitly listed.
Real media processing must be read-only.
No recursive traversal unless explicitly approved.
No batch traversal unless explicitly approved.
No upload is allowed.
No destructive write is allowed.
No modification of source files is allowed.
Output location must be controlled.
Report content must avoid leaking sensitive names if required.
Execution must be reproducible.
Failure paths must be safe.

PRODUCT_RUNTIME_REQUIREMENTS:
Read-only source handling.
Controlled output path.
Clear error messages.
Safe failure behavior.
No hidden network access.
No destructive file operations.
No accidental recursive scan.
No customer data committed to repository.
No secrets committed.
No real material committed.
Operator-visible report.
Human-readable logs.
Known dependency requirements.
Known platform assumptions.

INSTALLATION_REQUIREMENTS:
Define whether product is CLI, desktop app, or packaged local agent.
Define supported operating systems.
Define dependency strategy for FFmpeg and ffprobe.
Define model dependency strategy if transcription is later added.
Define update strategy.
Define uninstall strategy.
Define log location.
Define output location.
Define local configuration strategy.
Define environment separation from development repo.

LICENSING_REQUIREMENTS:
Define commercial model.
Define seat model.
Define device activation model.
Define offline grace period.
Define revocation strategy.
Define license check behavior.
Define privacy implications of activation.
Define what happens when license validation fails.
Define customer support responsibility.

SUPPORT_AND_OPERATIONS_REQUIREMENTS:
Define support contact.
Define support hours.
Define failure escalation.
Define known limitations.
Define backup expectations.
Define customer responsibility.
Define operator responsibility.
Define issue reporting format.
Define version identification.
Define rollback plan.
Define safe stop procedure.

PRODUCTION_ACCEPTANCE_REQUIREMENTS:
Private beta evidence reviewed.
Real-media controlled execution evidence reviewed.
Privacy and data-handling gate closed.
Installation and dependency strategy closed.
Packaging QA closed.
Known limitations documented.
Support model documented.
Rollback plan documented.
Customer scope documented.
Final production use acceptance gate explicitly closed.

CURRENTLY_NOT_APPROVED:
Production use is not approved.
Paid delivery is not approved.
Private pilot execution is not approved.
Real media processing is not approved.
Customer material processing is not approved.
Folder scanning is not approved.
Batch processing is not approved.
Recursive traversal is not approved.
Transcription is not approved.
Subtitles are not approved.
Sync is not approved.
DaVinci Resolve integration is not approved.
Avid integration is not approved.
SaaS integration is not approved.
Installer delivery is not approved.
Binary distribution is not approved.

SAFETY_CONFIRMATION:
No real media is allowed in this gate.
No customer material is allowed in this gate.
No production material is allowed in this gate.
No confidential material is allowed in this gate.
No FFmpeg is allowed in this gate.
No ffprobe is allowed in this gate.
No scanner integration is allowed in this gate.
No batch traversal is allowed in this gate.
No recursive traversal is allowed in this gate.
No SaaS module is allowed in this gate.
No database is allowed in this gate.
No backend change is allowed in this gate.
No frontend change is allowed in this gate.
No Docker change is allowed in this gate.
No Alembic change is allowed in this gate.
No Stripe change is allowed in this gate.
No AI Jobs change is allowed in this gate.
No credits or ledger change is allowed in this gate.
No installer is created in this gate.
No binary is created in this gate.

ALLOWED_SCOPE:
Add this production use path scope document.
Add one production use path scope unit test.
Inspect existing customer demo meeting pack document.
Inspect existing customer demo human review gate document.
Inspect existing tests.
Run validation tests.
Run WSL repo guard.
Run PostgreSQL-only regression guard required by policy.
Commit, tag, and push after validation.

FORBIDDEN_SCOPE:
No production approval.
No paid delivery approval.
No private pilot execution.
No prospect data capture yet.
No meeting pack edits.
No implementation changes.
No parser changes.
No CLI behavior changes.
No wrapper changes.
No renderer changes.
No fixture modification.
No committed export artifact.
No execution against real media.
No execution against customer material.
No FFmpeg.
No ffprobe.
No scanner integration.
No batch processing.
No recursive traversal.
No unsafe shell execution.
No pyproject modification.
No console script registration.
No SaaS integration.
No database access.
No backend changes.
No frontend changes.
No installer work.
No binary packaging.
No Docker work.
No Alembic work.
No Stripe work.
No AI Jobs work.
No credits or ledger work.

PASS_CRITERIA:
Production target final status is defined.
Current allowed use is explicit.
Current forbidden use is explicit.
Production use definition is explicit.
Mandatory path to production is listed.
Non-negotiable production blockers are listed.
Prospect feedback requirements are listed.
Private pilot boundary requirements are listed.
Real-media preflight requirements are listed.
Product runtime requirements are listed.
Installation requirements are listed.
Licensing requirements are listed.
Support and operations requirements are listed.
Production acceptance requirements are listed.
Currently not approved items are explicit.
Safety confirmation is explicit.
Allowed scope is explicit.
Forbidden scope is explicit.
No implementation change is performed.
No real media is used.
No customer material is used.
No installer is created.
No binary is created.

NEXT_RECOMMENDED_PHASE:
CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PROSPECT_FEEDBACK_CAPTURE.READINESS.GATE.V1

NEXT_RECOMMENDED_RESULT:
LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PROSPECT_FEEDBACK_CAPTURE_READINESS_GATE_V1_CLOSED

SUGGESTED_COMMIT:
docs: add CID Local Media Agent production use path scope gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-customer-demo-production-use-path-scope-gate-v1-20260701
