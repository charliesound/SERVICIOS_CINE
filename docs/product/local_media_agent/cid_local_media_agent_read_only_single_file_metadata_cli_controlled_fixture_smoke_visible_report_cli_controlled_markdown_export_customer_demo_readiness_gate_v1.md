# CID Local Media Agent - Customer Demo Readiness Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.READINESS.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_READINESS_GATE_V1_CLOSED

BASE_HEAD:
6c02de7ae0fe7d7c3effb144b4f3683fc6278949

BASE_COMMIT:
6c02de7 test: add CID Local Media Agent manual demo execution QA gate

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-manual-demo-execution-qa-gate-v1-20260701

STATUS:
READY_FOR_CONTROLLED_CUSTOMER_DEMO_SCRIPT_REVIEW

PURPOSE:
Doc/test-only readiness gate for a safe customer-facing controlled demo.

This gate prepares what may be shown to a trusted prospective customer.
This gate keeps the demo limited to a non-customer controlled fixture.
This gate does not approve real media usage.
This gate does not approve customer material usage.
This gate does not approve production use.
This gate does not add runtime behavior.

PRODUCT_POSITIONING:
CID Local Media Agent is being prepared as a local-first media utility for audiovisual teams.
At this stage, the customer demo must be presented as a controlled technical preview.
The demo proves that the public wrapper can read one controlled file, validate expected metadata, render a visible Markdown report, and export that report inside a controlled temporary root.

CUSTOMER_DEMO_ALLOWED_MESSAGE:
This is an early controlled preview of the Local Media Agent report flow.
It shows the future direction of local media inspection and report generation.
The current demo uses a safe internal fixture, not real production footage.
The current demo proves the wrapper, validation path, visible report rendering, controlled export policy, verification commands, cleanup, and evidence chain.

CUSTOMER_DEMO_FORBIDDEN_MESSAGE:
Do not claim that real camera media is supported yet.
Do not claim that real sound files are supported yet.
Do not claim that full folder scanning is supported yet.
Do not claim that batch processing is supported yet.
Do not claim that recursive traversal is supported yet.
Do not claim that audiovisual metadata extraction is supported yet.
Do not claim that transcription is supported yet.
Do not claim that sync by waveform, timecode, or slate is supported yet.
Do not claim that DaVinci Resolve or Avid integration is supported yet.
Do not claim that cloud upload is supported.
Do not claim that customer files can already be processed.
Do not claim that this is a production-ready release.

CUSTOMER_DEMO_ALLOWED_AUDIENCE:
Trusted prospective producer.
Trusted production executive.
Trusted postproduction supervisor.
Trusted internal stakeholder.
Owner/operator controlled presentation only.

CUSTOMER_DEMO_FORBIDDEN_AUDIENCE:
Public launch audience.
Unsupervised customer user.
Paid customer delivery.
School workshop with participant files.
Production team using real shooting material.
Any audience requiring support for confidential media.

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

CONTROLLED_OUTPUT_ROOT:
tests/tmp/local_media_agent/controlled_visible_report_exports

CUSTOMER_DEMO_EXPORT_FILE:
tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

CUSTOMER_DEMO_STDOUT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown

CUSTOMER_DEMO_EXPORT_PREP_COMMAND:
mkdir -p tests/tmp/local_media_agent/controlled_visible_report_exports

CUSTOMER_DEMO_EXPORT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown --visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

EXPECTED_EXPORT_STDOUT:
CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK

CUSTOMER_DEMO_VERIFICATION_TARGETS:
CID Local Media Agent - Controlled Fixture Smoke Visible Report
controlled_plain_text_marker_v1
media/controlled_plain_text_marker.txt
239
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

CUSTOMER_DEMO_CLEANUP_COMMAND:
rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports

CUSTOMER_DEMO_TALK_TRACK:
Step 1: Explain that this is a controlled local-only preview.
Step 2: Show the controlled fixture path and explain that it is not customer material.
Step 3: Run the public wrapper command.
Step 4: Show the visible Markdown report in stdout.
Step 5: Run the controlled export command.
Step 6: Verify that the exported Markdown report exists inside the controlled temporary root.
Step 7: Verify the controlled path and expected digest in the report.
Step 8: Record the generated report digest if needed.
Step 9: Clean the temporary export root.
Step 10: Show that the workspace is clean.

CUSTOMER_DEMO_STOP_CONDITIONS:
Stop if the repository is not at the expected stable base.
Stop if the workspace is not clean before the demo.
Stop if the target path is not the controlled fixture path.
Stop if the output path is not inside the controlled temporary export root.
Stop if the output suffix is not .md.
Stop if any customer or real media path appears.
Stop if the wrapper does not return the expected export success marker.
Stop if report verification fails.
Stop if cleanup fails.
Stop if workspace final status is not clean.

PREVIOUS_EVIDENCE_CHAIN:
Manual demo execution stdout: CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK
Manual demo report size: 1795 bytes
Manual demo report digest: b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd
Manual demo execution QA stable head: 6c02de7ae0fe7d7c3effb144b4f3683fc6278949

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
Add this customer demo readiness document.
Add one customer demo readiness unit test.
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
test: add CID Local Media Agent customer demo readiness gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-readiness-gate-v1-20260701
