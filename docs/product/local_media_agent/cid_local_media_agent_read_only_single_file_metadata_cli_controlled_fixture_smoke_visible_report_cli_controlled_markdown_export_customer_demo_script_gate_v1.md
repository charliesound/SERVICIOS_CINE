# CID Local Media Agent - Customer Demo Script Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.SCRIPT.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_SCRIPT_GATE_V1_CLOSED

BASE_HEAD:
18febf1ddb65b286c5aecd5dba837799cf8f8adc

BASE_COMMIT:
18febf1 test: add CID Local Media Agent customer demo readiness gate

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-readiness-gate-v1-20260701

STATUS:
READY_FOR_CONTROLLED_CUSTOMER_DEMO_SCRIPTED_PRESENTATION_ONLY

PURPOSE:
Doc/test-only gate for the safe customer-facing demo script.

This gate defines how to present the controlled Local Media Agent demo.
This gate defines what may be shown.
This gate defines what must not be claimed.
This gate defines the safe command sequence.
This gate defines the commercial discovery questions.
This gate does not approve customer material.
This gate does not approve real media.
This gate does not approve production use.
This gate does not add runtime behavior.

DEMO_TYPE:
Controlled customer-facing technical preview.

DEMO_OWNER:
Owner/operator only.

DEMO_AUDIENCE:
Trusted producer.
Trusted executive producer.
Trusted production manager.
Trusted postproduction supervisor.
Trusted distributor or exhibitor technical stakeholder.
Trusted school decision-maker without student files.

DEMO_NOT_FOR:
Public launch.
Paid delivery.
Unsupervised installation.
Workshop with participant media.
Real project ingestion.
Customer file processing.
Production workflow replacement.

OPENING_SCRIPT:
I want to show you a controlled preview of CID Local Media Agent.
The product direction is local-first: the files stay on the customer machine.
Today I am not going to process real footage or real sound.
This demo uses a safe internal fixture so we can verify the report flow without exposing any confidential material.
What you will see is the first validated chain: wrapper command, metadata validation, visible Markdown report, controlled export, verification, cleanup, and evidence.

VALUE_PROPOSITION_SCRIPT:
The problem this product will solve is the lack of fast, local, auditable visibility over audiovisual material.
Production and post teams often receive folders with mixed, unclear, or poorly documented assets.
The long-term goal is to help teams understand what is in a project folder before they start organizing, syncing, transcribing, editing, or delivering.
The current controlled demo proves a small but important foundation: a safe local command can inspect one allowed file, validate expected properties, and generate a readable report without sending material anywhere.

WHAT_TO_SHOW:
Show the repository is at the expected stable base.
Show the workspace is clean.
Show the controlled fixture path.
Explain that the fixture is not customer material.
Run the stdout visible report command.
Point out the report title.
Point out the allowed relative path.
Point out the expected byte count.
Point out the expected digest.
Run the controlled Markdown export command.
Verify the exported report exists inside the controlled temporary root.
Verify the report content.
Record the generated report digest if needed.
Clean the temporary export root.
Show final workspace clean status.

WHAT_NOT_TO_SHOW:
Do not show real camera files.
Do not show real sound files.
Do not show confidential project folders.
Do not show customer material.
Do not show private scripts or contracts.
Do not show SaaS internals.
Do not show database internals.
Do not show unrelated modules.
Do not show implementation source unless explicitly needed for technical due diligence.
Do not show future features as if they already work.

SAFE_DEMO_COMMANDS:
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

DEMO_TIMING_GUIDE:
Minute 0: Explain local-first product direction.
Minute 1: State the hard limitation: controlled fixture only.
Minute 2: Show clean repo state and controlled fixture path.
Minute 3: Run visible report to stdout.
Minute 4: Explain report fields.
Minute 5: Run controlled Markdown export.
Minute 6: Verify exported report and digest.
Minute 7: Clean temporary export root.
Minute 8: Explain roadmap without overclaiming.
Minute 9: Ask discovery questions.
Minute 10: Agree next safe step.

COMMERCIAL_DISCOVERY_QUESTIONS:
How many productions do you usually supervise at the same time?
Where do you currently lose time when receiving camera, sound, or postproduction material?
Who is responsible for checking whether folders are complete and understandable?
Do you receive material from different teams, units, cameras, sound mixers, or editors?
What is the most painful moment: ingest, sync, transcriptions, subtitles, delivery, or archive?
Would a local report before upload or handoff reduce risk for your team?
Would you prefer this as a local app, CLI tool, or integrated CID module?
How sensitive is your material from a confidentiality perspective?
Who would approve a paid pilot inside your company?
What would the first useful pilot need to prove before you pay for it?

ROADMAP_EXPLANATION_ALLOWED:
The current demo is intentionally small and controlled.
The next product steps can expand toward real media preflight, metadata extraction, folder-level reports, transcription, subtitles, sync assistance, and postproduction handoff.
Each step must be gated separately before it is presented as working functionality.
For paid pilots, scope must be limited, explicit, and validated with non-destructive local processing.

ROADMAP_EXPLANATION_FORBIDDEN:
Do not say real media processing is ready.
Do not say folder scanning is ready.
Do not say transcription is ready.
Do not say subtitles are ready.
Do not say sync is ready.
Do not say DaVinci Resolve integration is ready.
Do not say Avid integration is ready.
Do not say cloud collaboration is ready.
Do not say licensing or installer delivery is ready.
Do not say this replaces DIT, assistant editor, sound editorial, or post supervisor work.

SAFE_CLOSE_SCRIPT:
This is not yet a production product.
What I wanted to validate with you today is whether this local-first direction solves a real operational pain.
The current working proof is the controlled report chain.
If this is useful, the next safe step would be defining a private pilot with strict boundaries, no destructive actions, and no cloud upload of sensitive files.

STOP_CONDITIONS:
Stop if the repository is not at the expected stable base.
Stop if the workspace is not clean before the demo.
Stop if the target path is not the controlled fixture path.
Stop if the output path is not inside the controlled temporary export root.
Stop if the output suffix is not .md.
Stop if any customer or real media path appears.
Stop if the wrapper does not return the expected success marker.
Stop if report verification fails.
Stop if cleanup fails.
Stop if workspace final status is not clean.
Stop if the audience asks to process real material during this gate.
Stop if the audience interprets the demo as production-ready.

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
Add this customer demo script document.
Add one customer demo script unit test.
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
test: add CID Local Media Agent customer demo script gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-script-gate-v1-20260701
