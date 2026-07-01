# CID Local Media Agent - Manual Demo Readiness Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.MANUAL_DEMO.READINESS.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_MANUAL_DEMO_READINESS_GATE_V1_CLOSED

BASE_HEAD:
0f220e872ff5f0804dbffe2f8b5934787d5d775f

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-controlled-demo-execution-qa-gate-v1-20260701

STATUS:
READY_FOR_MANUAL_CONTROLLED_FIXTURE_DEMO_ONLY

PURPOSE:
Doc/test-only readiness gate for a safe manual controlled fixture demo.

This is internal owner/operator only.
This is not a customer demo gate.
This is not a real media gate.

WRAPPER:
scripts/local_media_agent/read_only_single_file_metadata_cli.py

IMPLEMENTATION:
scripts/local_media_agent/read_only_single_file_metadata.py

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

EXPECTED_SHA256:
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

CONTROLLED_OUTPUT_ROOT:
tests/tmp/local_media_agent/controlled_visible_report_exports

MANUAL_DEMO_EXPORT_FILE:
tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md

VISIBLE_STDOUT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown

CONTROLLED_EXPORT_PREP_COMMAND:
mkdir -p tests/tmp/local_media_agent/controlled_visible_report_exports

CONTROLLED_EXPORT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown --visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md

EXPECTED_EXPORT_STDOUT:
CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK

EXPECTED_VISIBLE_REPORT_EVIDENCE:
CID Local Media Agent - Controlled Fixture Smoke Visible Report
controlled_plain_text_marker_v1
media/controlled_plain_text_marker.txt
239
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

VERIFICATION_COMMANDS:
test -f tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md
grep -F "CID Local Media Agent - Controlled Fixture Smoke Visible Report" tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md
grep -F "media/controlled_plain_text_marker.txt" tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md
grep -F "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a" tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md
sha256sum tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md

CLEANUP_COMMAND:
rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports

SAFETY_CHECKLIST_BEFORE:
Confirm current directory is /opt/SERVICIOS_CINE.
Confirm virtual environment is active.
Confirm git status is clean.
Confirm the demo uses only the controlled fixture.
Confirm the output file is inside tests/tmp/local_media_agent/controlled_visible_report_exports.
Confirm the output suffix is .md.
Confirm no real media path is used.
Confirm no customer material path is used.
Confirm no repo-root report path is used.

SAFETY_CHECKLIST_AFTER:
Confirm stdout is CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK for export mode.
Confirm manual_demo_visible_report.md exists only inside the controlled output root.
Confirm the report contains the expected controlled fixture SHA256.
Confirm the report contains media/controlled_plain_text_marker.txt.
Remove tests/tmp/local_media_agent/controlled_visible_report_exports.
Confirm git status is clean.

ALLOWED_SCOPE:
Add this readiness document.
Add one readiness unit test.
Inspect existing files.
Inspect implementation parser read-only.
Inspect controlled fixture integrity.
Keep this phase doc/test-only.

FORBIDDEN_SCOPE:
No implementation changes.
No parser changes.
No CLI behavior changes.
No wrapper changes.
No renderer changes.
No in-memory integration changes.
No subprocess in this readiness test.
No execution against real material.
No execution against customer material.
No manual demo artifact committed.
No persistent output artifacts.
No export outside controlled test root.
No fixture modification.
No scanner integration.
No batch processing.
No recursive product traversal.
No FFmpeg.
No ffprobe.
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

REQUIRED_VALIDATION_COMMANDS:
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_readiness_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
bash scripts/dev/guard_wsl_repo.sh
Mandatory PostgreSQL-only regression guard.

SUGGESTED_COMMIT:
test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export manual demo readiness gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-manual-demo-readiness-gate-v1-20260701
