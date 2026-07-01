# CID Local Media Agent - Customer Demo Packaging Readiness Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PACKAGING.READINESS.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_PACKAGING_READINESS_GATE_V1_CLOSED

BASE_HEAD:
a13d20b89beb39f5468785d93767c76edd3eefb7

BASE_COMMIT:
a13d20b test: add CID Local Media Agent customer demo execution QA gate

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-qa-gate-v1-20260701

STATUS:
READY_FOR_SAFE_CUSTOMER_DEMO_MEETING_PACK_ONLY

PURPOSE:
Doc/test-only readiness gate for a safe customer demo meeting package.

This gate prepares the meeting package.
This gate does not create an installer.
This gate does not create binaries.
This gate does not package customer files.
This gate does not approve real media processing.
This gate does not approve customer material processing.
This gate does not add runtime behavior.
This gate does not approve production use.
This gate does not approve paid delivery.

MEETING_PACKAGE_TYPE:
Controlled customer demo meeting pack.

MEETING_PACKAGE_OWNER:
Owner/operator only.

MEETING_PACKAGE_ALLOWED_USE:
One-to-one trusted prospect meeting.
Private producer meeting.
Private executive producer meeting.
Private postproduction supervisor meeting.
Private distributor or exhibitor technical discussion.
Private school decision-maker meeting without participant files.

MEETING_PACKAGE_FORBIDDEN_USE:
Public launch.
Paid delivery.
Downloadable product distribution.
Unsupervised installation.
Workshop with participant media.
Real project ingestion.
Customer file processing.
Production workflow replacement.

EXECUTIVE_SUMMARY:
CID Local Media Agent is being prepared as a local-first utility for audiovisual teams.
The current controlled demo proves a small but important foundation: one safe command can inspect one allowed internal fixture, validate expected properties, render a visible Markdown report, export it inside a controlled temporary root, verify it, clean it, and leave a clean workspace.
The current demo is not a production product.
The current demo is not a real-media processor.
The current demo is a controlled proof of the future local report chain.

ONE_SENTENCE_PITCH:
CID Local Media Agent aims to help film and postproduction teams understand audiovisual material locally before ingest, sync, transcription, edit, delivery, or archive.

SHORT_MEETING_SCRIPT:
This is a controlled preview, not a production release.
The product direction is local-first: files stay on the client machine.
Today I will only show a safe internal fixture.
I will not process real footage, real sound, confidential files, or customer material.
The proof today is the controlled report chain: validation, visible report, controlled export, verification, cleanup, and evidence.

WHAT_THE_DEMO_PROVES:
The public wrapper can be executed safely.
The controlled fixture can be validated by path, size, and digest.
A visible Markdown report can be generated.
A Markdown report can be exported only into a controlled temporary root.
The report can be verified.
The generated report digest can be recorded.
The temporary export root can be removed.
The workspace can remain clean.
The evidence chain can be audited.

WHAT_THE_DEMO_DOES_NOT_PROVE:
It does not prove real camera media processing.
It does not prove real sound file processing.
It does not prove folder scanning.
It does not prove batch processing.
It does not prove recursive traversal.
It does not prove audiovisual metadata extraction.
It does not prove transcription.
It does not prove subtitles.
It does not prove sync.
It does not prove DaVinci Resolve integration.
It does not prove Avid integration.
It does not prove SaaS integration.
It does not prove installer delivery.
It does not prove production readiness.

SAFE_DEMO_COMMANDS_INCLUDED_IN_PACK:
STDOUT_REPORT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown

EXPORT_REPORT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown --visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

VERIFY_REPORT_COMMANDS:
test -f tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "CID Local Media Agent - Controlled Fixture Smoke Visible Report" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "media/controlled_plain_text_marker.txt" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
sha256sum tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

CLEANUP_COMMAND:
rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports

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

LAST_EXECUTION_EVIDENCE:
Controlled customer demo execution result: LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS
Generated report size: 1795 bytes
Generated report digest: b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd
Controlled fixture digest: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a
Final workspace: clean

MEETING_ASSETS_ALLOWED:
Executive summary text.
One-sentence pitch.
Short meeting script.
Safe demo command sequence.
Demo limitation list.
Discovery questions.
Go/no-go checklist.
Follow-up options.
Evidence summary from the controlled execution QA gate.

MEETING_ASSETS_FORBIDDEN:
Installer package.
Executable package.
Binary distribution.
Customer media sample.
Real camera file.
Real sound file.
Confidential project folder.
SaaS credentials.
Database access.
Backend screen.
Frontend screen.
Cloud upload workflow.
Production-ready claim.

DISCOVERY_QUESTIONS_FOR_MEETING:
How many productions do you supervise at the same time?
Where do you currently lose time when receiving camera, sound, or postproduction material?
Who checks whether folders are complete and understandable?
Do you receive material from several cameras, sound mixers, units, editors, or vendors?
Would a local report before upload or handoff reduce operational risk?
What would be the first useful real-media preflight your team would pay for?
Who would approve a private pilot?
What material types would a future pilot need to support?
What cannot leave your premises under any circumstance?
Would you prefer a local app, CLI tool, or CID-integrated module?

SAFE_FOLLOW_UP_OPTIONS:
Schedule a requirements call.
Define a private pilot boundary.
Identify first real-media preflight requirements.
Collect requirements without taking customer files.
Ask for non-sensitive synthetic examples only.
Define success criteria for a future paid pilot.
Define who approves technical pilots.

MEETING_STOP_CONDITIONS:
Stop if the prospect asks to process real material during this controlled pack stage.
Stop if the prospect asks to send customer files.
Stop if the prospect interprets the demo as production-ready.
Stop if the operator cannot explain current limitations clearly.
Stop if the workspace is not clean.
Stop if the repo is not at the expected stable state.
Stop if the controlled fixture path is changed.
Stop if the export path leaves the controlled temporary root.
Stop if the report verification fails.
Stop if cleanup fails.

PACKAGING_READINESS_PASS_CRITERIA:
Executive summary is present.
One-sentence pitch is present.
Short meeting script is present.
Safe command sequence is present.
Controlled fixture identity is present.
Last execution evidence is present.
Limitations are explicit.
Allowed meeting assets are explicit.
Forbidden meeting assets are explicit.
Discovery questions are present.
Safe follow-up options are present.
Stop conditions are present.
No real material is included.
No customer material is included.
No generated report artifact is committed.
No installer or binary package is created.

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
No installer is created.
No binary is created.

ALLOWED_SCOPE:
Add this customer demo packaging readiness document.
Add one customer demo packaging readiness unit test.
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
No binary packaging.
No Docker work.
No Alembic work.
No Stripe work.
No AI Jobs work.
No credits or ledger work.

REQUIRED_VALIDATION_TARGETS:
Customer demo packaging readiness gate test.
Customer demo execution QA gate test.
Customer demo execution gate test.
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
test: add CID Local Media Agent customer demo packaging readiness gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-readiness-gate-v1-20260701
