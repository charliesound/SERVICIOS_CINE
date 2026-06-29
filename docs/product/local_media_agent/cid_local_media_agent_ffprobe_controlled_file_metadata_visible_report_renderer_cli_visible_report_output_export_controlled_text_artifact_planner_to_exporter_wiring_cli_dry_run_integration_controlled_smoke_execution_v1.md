# CID Local Media Agent — FFprobe controlled file metadata visible report renderer CLI visible report output export controlled text artifact planner to exporter wiring CLI dry-run integration controlled smoke execution v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.V1`

## Smoke execution result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_SMOKE_EXECUTION_PASS_READY_FOR_QA_GATE`

## Smoke execution date

2026-06-29

## Smoke execution type

This is a controlled smoke execution.

This smoke execution validates the controlled CLI dry-run integration through the Python entrypoint with inline controlled arguments.

This smoke execution does not write files.

This smoke execution does not create directories.

This smoke execution does not create artifacts on disk.

This smoke execution does not use real media.

This smoke execution does not scan folders.

This smoke execution does not execute ffprobe.

This smoke execution does not execute FFmpeg.

This smoke execution does not execute external processes.

This smoke execution does not access networks.

This smoke execution does not touch SaaS, database, backend, frontend, installer, client demo, public demo, or production code.

## Previous stable state

Previous stable commit:

`6881ac27f00daf0b31c555955b322aa11b68370a`

Previous stable tag:

`cid-dev-stable-local-media-agent-cli-dry-run-controlled-impl-qa-closure-review-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-v1-20260629`

## Files in scope

Only these files are in scope for this controlled smoke execution:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution.py`

No other files are in scope.

## Artifacts under smoke execution

The controlled CLI module under smoke execution is:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py`

The controlled CLI implementation test under smoke execution is:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation.py`

The controlled CLI implementation QA gate closure review under smoke execution is:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_closure_review_v1.md`

The controlled dry-run bridge under smoke execution is:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py`

## Previous validation evidence accepted

The controlled implementation QA gate closure review was accepted because the recorded validation included:

- target CLI dry-run controlled implementation QA gate closure review test passed with 113 checks.
- controlled implementation QA gate test passed with 145 checks.
- controlled implementation test passed with 41 checks.
- py_compile passed.
- exact staged files check passed.
- staged diff check passed.
- restricted database word check passed.
- new CLI forbidden marker check passed.
- WSL guard passed.
- database regression guard passed.
- target controlled implementation QA closure review short tag absent locally before tagging.
- target controlled implementation QA closure review short tag absent remotely before tagging.
- commit completed.
- local tag completed.
- push main completed.
- push tag completed.
- post-push verification completed.
- final target closure review test passed with 113 checks.
- final controlled implementation QA gate test passed with 145 checks.
- final controlled implementation test passed with 41 checks.
- final new CLI forbidden marker check passed.
- working tree was clean after post-push verification.

## Controlled smoke execution scope

This smoke execution uses controlled inline visible report text.

This smoke execution uses controlled inline planner result JSON.

This smoke execution uses controlled inline caller context JSON.

This smoke execution invokes `main(...)` directly with controlled arguments.

This smoke execution captures stdout.

This smoke execution parses stdout as deterministic JSON.

This smoke execution verifies exit code `0`.

This smoke execution verifies `cli_decision=CONTROLLED_CLI_DRY_RUN_ACCEPTED`.

This smoke execution verifies `dry_run=True`.

This smoke execution verifies `write_requested=False`.

This smoke execution verifies `write_performed=False`.

This smoke execution verifies `artifact_created_on_disk=False`.

This smoke execution verifies bridge `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED`.

This smoke execution verifies no stderr output on accepted dry-run.

This smoke execution verifies fail-closed behavior for invalid planner JSON.

This smoke execution verifies fail-closed behavior for missing `--dry-run`.

This smoke execution verifies fail-closed behavior for forbidden operational flags.

## Controlled smoke execution accepted boundaries

The controlled smoke execution is accepted only because it does not write files.

The controlled smoke execution is accepted only because it does not create directories.

The controlled smoke execution is accepted only because it does not create artifacts on disk.

The controlled smoke execution is accepted only because it does not read files.

The controlled smoke execution is accepted only because it does not read real media.

The controlled smoke execution is accepted only because it does not scan folders.

The controlled smoke execution is accepted only because it does not execute ffprobe.

The controlled smoke execution is accepted only because it does not execute FFmpeg.

The controlled smoke execution is accepted only because it does not execute external processes.

The controlled smoke execution is accepted only because it does not access networks.

The controlled smoke execution is accepted only because it uses inline controlled arguments.

The controlled smoke execution is accepted only because it emits JSON to stdout.

## Smoke rejection conditions

This smoke execution must fail if:

- accepted dry-run exits with a non-zero code.
- accepted dry-run writes to stderr.
- accepted dry-run emits non-JSON stdout.
- accepted dry-run omits the phase.
- accepted dry-run omits the functional result.
- accepted dry-run omits the next safe phase.
- accepted dry-run omits the CLI decision.
- accepted dry-run omits bridge result.
- accepted dry-run claims write_requested true.
- accepted dry-run claims write_performed true.
- accepted dry-run claims artifact_created_on_disk true.
- accepted dry-run claims a bridge decision other than CONTROLLED_DRY_RUN_ACCEPTED.
- invalid planner JSON fails open.
- missing `--dry-run` fails open.
- forbidden operational flags fail open.
- the CLI source exposes write options.
- the CLI source exposes output file options.
- the CLI source contains file write markers.
- the CLI source contains directory creation markers.
- the CLI source contains network markers.
- the CLI source contains external process markers.

## Explicit non-authorization

This smoke execution does not authorize write-enabled export.

This smoke execution does not authorize directory creation.

This smoke execution does not authorize artifact creation on disk.

This smoke execution does not authorize real file writing.

This smoke execution does not authorize media scanning.

This smoke execution does not authorize real media decoding.

This smoke execution does not authorize ffprobe execution.

This smoke execution does not authorize FFmpeg execution.

This smoke execution does not authorize external process execution.

This smoke execution does not authorize audio extraction.

This smoke execution does not authorize sync.

This smoke execution does not authorize transcription.

This smoke execution does not authorize subtitle generation.

This smoke execution does not authorize timeline export.

This smoke execution does not authorize network access.

This smoke execution does not authorize SaaS integration.

This smoke execution does not authorize database changes.

This smoke execution does not authorize backend changes.

This smoke execution does not authorize frontend changes.

This smoke execution does not authorize installer work.

This smoke execution does not authorize public demo work.

This smoke execution does not authorize client-facing demo work.

This smoke execution does not authorize production use.

## Smoke execution decision

The controlled CLI dry-run smoke execution is accepted.

The controlled CLI dry-run can execute with inline controlled values.

The controlled CLI dry-run emits deterministic JSON stdout.

The controlled CLI dry-run fails closed for invalid inputs.

The controlled CLI dry-run remains restricted to dry-run-only behavior.

The project is ready for a future controlled smoke execution QA gate.

The project is not ready for write-enabled export behavior.

The project is not ready for directory creation.

The project is not ready for artifact creation on disk.

The project is not ready for real media execution.

The project is not ready for public, client-facing, or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.QA.GATE.V1`

That next step must remain doc/test-only.
