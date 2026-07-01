# CID Local Media Agent - Customer Demo Execution Readiness Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.EXECUTION.READINESS.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_EXECUTION_READINESS_GATE_V1_CLOSED

BASE_HEAD:
aad24d1f08f5a071f0568f0116744763720d2f91

BASE_COMMIT:
aad24d1 test: add CID Local Media Agent customer demo script gate

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-script-gate-v1-20260701

STATUS:
READY_FOR_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PREFLIGHT_ONLY

PURPOSE:
Doc/test-only readiness gate for executing the scripted controlled customer demo.

This gate prepares the execution checklist.
This gate prepares the operator preflight.
This gate prepares the exact screen order.
This gate prepares the evidence to capture after execution.
This gate does not execute the customer demo.
This gate does not approve customer material.
This gate does not approve real media.
This gate does not approve production use.
This gate does not add runtime behavior.

EXECUTION_TYPE:
Controlled customer-facing scripted presentation readiness.

EXECUTION_OWNER:
Owner/operator only.

EXECUTION_AUDIENCE_ALLOWED:
Trusted producer.
Trusted executive producer.
Trusted production manager.
Trusted postproduction supervisor.
Trusted distributor or exhibitor technical stakeholder.
Trusted school decision-maker without participant files.

EXECUTION_AUDIENCE_FORBIDDEN:
Public launch audience.
Paid delivery audience.
Unsupervised user.
Workshop participants using their own files.
Real project team using production material.
Any audience expecting production-ready processing.

PRE_DEMO_PREFLIGHT_CHECKLIST:
Confirm working directory is /opt/SERVICIOS_CINE.
Confirm virtual environment is active.
Confirm branch is main.
Confirm HEAD is aad24d1f08f5a071f0568f0116744763720d2f91.
Confirm stable script gate tag points to the same HEAD.
Confirm workspace is clean.
Confirm no export root exists before the demo.
Confirm the target path is the controlled fixture path.
Confirm the output path is inside the controlled temporary export root.
Confirm the output suffix is .md.
Confirm no real media path is present.
Confirm no customer material path is present.
Confirm no production folder path is present.
Confirm no external upload is involved.
Confirm no SaaS screen is opened.
Confirm no database screen is opened.

OPERATOR_OPENING_LINE:
This is a controlled local-first technical preview using an internal non-customer fixture only.

OPERATOR_BOUNDARY_LINE:
I will not process real footage, real sound, confidential files, or customer material in this demo.

OPERATOR_VALUE_LINE:
The useful proof today is the controlled report chain: validation, visible Markdown report, controlled export, verification, cleanup, and evidence.

SCREEN_ORDER:
Screen 1: Terminal inside /opt/SERVICIOS_CINE.
Screen 2: Show current stable HEAD and clean workspace.
Screen 3: Show controlled fixture path.
Screen 4: Run visible report to stdout.
Screen 5: Explain report title, allowed relative path, byte count, and digest.
Screen 6: Prepare controlled temporary export root.
Screen 7: Run controlled Markdown export.
Screen 8: Verify exported report exists inside controlled temporary export root.
Screen 9: Verify report title, allowed relative path, and digest.
Screen 10: Capture generated report digest.
Screen 11: Remove controlled temporary export root.
Screen 12: Show final clean workspace.
Screen 13: Ask discovery questions from the script gate.
Screen 14: Close with private pilot boundary discussion.

SAFE_COMMAND_SEQUENCE:
PRECHECK_STATUS:
git status --short
git rev-parse HEAD
git branch --show-current
git tag --points-at HEAD

PRECHECK_EXPORT_ROOT:
test ! -e tests/tmp/local_media_agent/controlled_visible_report_exports

STDOUT_REPORT:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown

EXPORT_PREP:
mkdir -p tests/tmp/local_media_agent/controlled_visible_report_exports

EXPORT_REPORT:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown --visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

VERIFY_REPORT:
test -f tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "CID Local Media Agent - Controlled Fixture Smoke Visible Report" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "media/controlled_plain_text_marker.txt" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
sha256sum tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

CLEANUP:
rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports

FINAL_STATUS:
git status --short

EXPECTED_SUCCESS_MARKER:
CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK

CONTROLLED_FIXTURE_ROOT:
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

CONTROLLED_TARGET_PATH:
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

ALLOWED_RELATIVE_PATH:
media/controlled_plain_text_marker.txt

FIXTURE_ID:
controlled_plain_text_marker_v1

EXPECTED_BYTES:
239

EXPECTED_FIXTURE_SHA256:
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

EXPECTED_REPORT_TITLE:
CID Local Media Agent - Controlled Fixture Smoke Visible Report

CONTROLLED_EXPORT_ROOT:
tests/tmp/local_media_agent/controlled_visible_report_exports

CONTROLLED_EXPORT_FILE:
tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

POST_DEMO_EVIDENCE_TO_CAPTURE:
stdout success marker.
exported report file size.
exported report digest.
report title verification.
allowed relative path verification.
controlled fixture digest verification.
cleanup confirmation.
final clean workspace confirmation.
audience questions asked.
next-step decision.

DEMO_PASS_CRITERIA:
Repository is at expected stable base.
Workspace is clean before execution.
Only controlled fixture path is used.
Visible report command returns expected success marker or readable report.
Controlled export command returns expected success marker.
Exported report exists only inside controlled temporary export root.
Report contains expected title.
Report contains expected allowed relative path.
Report contains expected fixture digest.
Generated report digest is recorded.
Controlled temporary export root is removed.
Workspace is clean after execution.
No customer material appears.
No real media appears.
No production path appears.

DEMO_FAIL_CRITERIA:
Repository is not at expected stable base.
Workspace is dirty before execution.
Unexpected file appears in workspace.
Target path differs from controlled fixture path.
Output path leaves controlled temporary export root.
Output suffix is not .md.
Expected success marker is absent.
Report file is missing.
Report verification fails.
Cleanup fails.
Workspace is dirty after cleanup.
Audience asks to process real material and operator continues.
Audience interprets the demo as production-ready and operator does not correct it.

GO_NO_GO_DECISION:
GO only if every preflight item passes.
NO-GO if any stop condition is true.
NO-GO if customer material is requested.
NO-GO if real media processing is requested.
NO-GO if the operator cannot clearly explain the current limitations.

STOP_CONDITIONS:
Stop if the repository is not at the expected stable base.
Stop if the workspace is not clean before the demo.
Stop if the target path is not the controlled fixture path.
Stop if the output path is not inside the controlled temporary export root.
Stop if the output suffix is not .md.
Stop if any customer or real media path appears.
Stop if any production folder path appears.
Stop if the wrapper does not return the expected success marker.
Stop if report verification fails.
Stop if cleanup fails.
Stop if workspace final status is not clean.
Stop if the audience asks to process real material during this gate.
Stop if the audience interprets the demo as production-ready.

CUSTOMER_CLOSE_OPTIONS:
Option 1: Schedule a private requirements call.
Option 2: Define a paid pilot boundary.
Option 3: Identify the first real-media gate needed before a private pilot.
Option 4: Collect sample requirements without taking customer files.
Option 5: Ask who approves technical pilots.

NOT_ALLOWED_AFTER_DEMO:
Do not take customer media.
Do not promise immediate real-media processing.
Do not promise folder scanning.
Do not promise transcription.
Do not promise sync.
Do not promise subtitles.
Do not promise DaVinci Resolve integration.
Do not promise Avid integration.
Do not promise SaaS integration.
Do not promise installer delivery.
Do not promise production readiness.

SAFETY_CONFIRMATION:
No real media is allowed.
No customer material is allowed.
No production material is allowed.
No confidential material is allowed.
No FFmpeg is allowed.
No ffprobe is allowed.
No scanner integration is allowed.
No batch traversal is allowed.
No recursive traversal is allowed.
No SaaS module is allowed.
No database is allowed.
No backend change is allowed.
No frontend change is allowed.
No Docker change is allowed.
No Alembic change is allowed.
No Stripe change is allowed.
No AI Jobs change is allowed.
No credits or ledger change is allowed.
No committed customer demo export artifact is allowed.

ALLOWED_SCOPE:
Add this customer demo execution readiness document.
Add one customer demo execution readiness unit test.
Inspect existing documents.
Inspect existing tests.
Run validation tests.
Run WSL repo guard.
Run PostgreSQL-only regression guard required by policy.
Commit, tag, and push after validation.

FORBIDDEN_SCOPE:
No implementation changes.
No parser changes.
No CLI behavior changes.
No wrapper changes.
No renderer changes.
No in-memory integration changes.
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
No Docker work.
No Alembic work.
No Stripe work.
No AI Jobs work.
No credits or ledger work.

REQUIRED_VALIDATION_TARGETS:
Customer demo execution readiness gate test.
Customer demo script gate test.
Customer demo readiness gate test.
Manual demo execution QA gate test.
Manual demo execution gate test.
Manual demo readiness gate test.
Controlled demo execution QA gate test.
Controlled demo execution gate test.
Wrapper smoke execution QA gate test.
Wrapper smoke execution gate test.
Implementation QA gate test.
Implementation gate test.
In-memory wrapper smoke execution QA gate test.
In-memory wrapper smoke execution gate test.
Visible report contract test.
CLI contract gate test.
WSL repo guard.
PostgreSQL-only regression guard required by policy.

SUGGESTED_COMMIT:
test: add CID Local Media Agent customer demo execution readiness gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-readiness-gate-v1-20260701
