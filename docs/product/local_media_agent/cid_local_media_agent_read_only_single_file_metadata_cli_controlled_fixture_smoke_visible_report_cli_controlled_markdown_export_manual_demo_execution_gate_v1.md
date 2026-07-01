# CID Local Media Agent - Manual Demo Execution Gate V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.MANUAL_DEMO.EXECUTION.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_MANUAL_DEMO_EXECUTION_GATE_V1_CLOSED

BASE_HEAD:
437b906bc3dfe35404c321ec5d7eff7cac474500

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-manual-demo-readiness-gate-v1-20260701

STATUS:
MANUAL_CONTROLLED_FIXTURE_DEMO_EXECUTED_AND_VERIFIED

PURPOSE:
Record the successful manual execution of the safe controlled fixture demo.

This gate records evidence only.
This gate does not add runtime behavior.
This gate does not execute against real media.
This gate does not execute against customer material.

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

EXPECTED_FIXTURE_SHA256:
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

CONTROLLED_OUTPUT_ROOT:
tests/tmp/local_media_agent/controlled_visible_report_exports

MANUAL_DEMO_EXPORT_FILE:
tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md

MANUAL_EXECUTION_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown --visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md

MANUAL_EXECUTION_STDOUT:
CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK

GENERATED_REPORT_SIZE_BYTES:
1795

GENERATED_REPORT_SHA256:
b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd

VERIFIED_REPORT_EVIDENCE:
CID Local Media Agent - Controlled Fixture Smoke Visible Report
media/controlled_plain_text_marker.txt
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

CLEANUP_COMMAND_EXECUTED:
rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports

FINAL_WORKSPACE_STATUS:
clean

EXECUTION_RESULT:
PASS

CLOSURE_EVIDENCE:
The documented manual controlled fixture demo was executed from the public wrapper.
The wrapper returned CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.
The Markdown visible report was created inside the controlled temporary export root.
The report contained the expected controlled fixture path.
The report contained the expected controlled fixture SHA256.
The generated report SHA256 was recorded.
The controlled temporary export root was removed after verification.
The final workspace check was clean.

SAFETY_CONFIRMATION:
No real media was used.
No customer material was used.
No FFmpeg was used.
No ffprobe was used.
No scanner integration was used.
No batch traversal was used.
No recursive traversal was used.
No SaaS module was touched.
No database was touched.
No backend was touched.
No frontend was touched.
No Docker file was touched.
No Alembic migration was touched.
No Stripe code was touched.
No AI Jobs code was touched.
No credits or ledger code was touched.
No persistent manual demo artifact was committed.

ALLOWED_SCOPE:
Add this manual execution evidence document.
Add one manual execution evidence unit test.
Run validation tests.
Run WSL guard.
Run PostgreSQL-only regression guard.
Commit, tag, push after validation.

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

REQUIRED_VALIDATION_COMMANDS:
pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_execution_gate.py
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
bash scripts/dev/guard_no_sqlite_regressions.sh

SUGGESTED_COMMIT:
test: add CID Local Media Agent manual controlled demo execution gate

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-manual-demo-execution-gate-v1-20260701
