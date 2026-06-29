# CID Local Media Agent — FFprobe controlled file metadata visible report renderer CLI visible report output export controlled text artifact planner to exporter wiring CLI dry-run integration contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.CONTRACT.V1`

## Contract result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTRACT_PASS_READY_FOR_QA_GATE`

## Contract date

2026-06-29

## Contract type

This is a doc/test-only contract.

This contract defines the future CLI dry-run integration boundary.

This contract does not add CLI integration code.

This contract does not modify CLI argument parsing.

This contract does not modify CLI command routing.

This contract does not modify the controlled dry-run bridge.

This contract does not modify planner runtime code.

This contract does not modify exporter runtime code.

This contract does not authorize write-enabled behavior.

## Previous stable state

Previous stable commit:

`7ec53d5ee662eb4f8d8dc9f082483ec9d48394c2`

Previous stable tag:

`cid-dev-stable-local-media-agent-cli-dry-run-readiness-qa-closure-review-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.READINESS.GATE.QA.GATE.CLOSURE.REVIEW.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_READINESS_GATE_QA_GATE_CLOSURE_REVIEW_PASS_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-cli-dry-run-contract-v1-20260629`

## Files in scope

Only these files are in scope for this contract:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract.py`

No other files are in scope.

## Existing artifacts under contract review

The CLI dry-run readiness QA closure review artifact is:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_readiness_gate_qa_gate_closure_review_v1.md`

The controlled dry-run bridge artifact is:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py`

The controlled dry-run bridge test artifact is:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation.py`

## Previous validation evidence accepted

The CLI dry-run readiness QA closure review was accepted because the recorded validation included:

- target closure review test passed with 93 checks.
- previous CLI dry-run integration readiness QA gate test passed with 157 checks.
- previous CLI dry-run integration readiness gate test passed with 136 checks.
- py_compile passed.
- exact staged files check passed.
- staged diff check passed.
- restricted database word check passed.
- WSL guard passed.
- database regression guard passed.
- push main completed.
- short tag moved to validated HEAD.
- push short tag completed.
- old long remote tag was absent.
- post-push verification completed.
- working tree was clean after post-push verification.

## Future CLI command boundary

A future CLI dry-run integration may expose controlled dry-run exporter metadata through an existing or future CLI surface only after a later implementation readiness gate authorizes code.

The future CLI command must remain dry-run only.

The future CLI command must route to the controlled dry-run bridge without changing the bridge safety contract.

The future CLI command must not bypass planner validation.

The future CLI command must not bypass visible report text validation.

The future CLI command must not bypass filename suffix validation.

The future CLI command must not bypass planned artifact path validation.

The future CLI command must not bypass content hash validation.

The future CLI command must not bypass path boundary validation.

The future CLI command must not bypass safety flag validation.

The future CLI command must not bypass caller context sanitization.

## Future CLI input contract

A future CLI dry-run integration must receive or build a planner result that already satisfies the controlled dry-run bridge contract.

A future CLI dry-run integration must receive visible report text as controlled text input.

A future CLI dry-run integration must preserve `dry_run=True`.

A future CLI dry-run integration must preserve `write_requested=False`.

A future CLI dry-run integration must reject or fail closed for `write_requested=True`.

A future CLI dry-run integration must reject or fail closed for `dry_run=False`.

A future CLI dry-run integration must reject missing planner result fields.

A future CLI dry-run integration must reject unsafe path boundary data.

A future CLI dry-run integration must reject unsafe safety flag data.

A future CLI dry-run integration must reject content hash mismatch.

A future CLI dry-run integration must reject planner results that claim prior write execution.

A future CLI dry-run integration must reject planner results that claim prior artifact creation.

## Future CLI output contract

A future CLI dry-run integration must display `dry_run=True`.

A future CLI dry-run integration must display `write_performed=False`.

A future CLI dry-run integration must display `artifact_created_on_disk=False`.

A future CLI dry-run integration must display `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` when accepted.

A future CLI dry-run integration must display the planned artifact path as human-visible dry-run information only.

A future CLI dry-run integration must state that no file was written.

A future CLI dry-run integration must state that no artifact was created on disk.

A future CLI dry-run integration must not claim that an export was produced.

A future CLI dry-run integration must not claim that a directory was created.

A future CLI dry-run integration must not claim that an artifact exists on disk.

A future CLI dry-run integration must redact or avoid sensitive paths when required by existing privacy policy.

## Future CLI failure contract

A future CLI dry-run integration must fail closed.

A future CLI dry-run integration must surface bridge validation errors as controlled CLI errors.

A future CLI dry-run integration must not continue into write behavior after failure.

A future CLI dry-run integration must not create fallback artifacts after failure.

A future CLI dry-run integration must not create fallback directories after failure.

A future CLI dry-run integration must not execute media tools after failure.

A future CLI dry-run integration must not access the network after failure.

## Future CLI accepted success markers

A future accepted CLI dry-run output may include only controlled dry-run status markers such as:

- `dry_run=True`
- `write_requested=False`
- `write_performed=False`
- `artifact_created_on_disk=False`
- `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED`
- planned artifact path for review
- no file written
- no artifact created on disk

## Explicit non-authorization

This contract does not authorize CLI integration code.

This contract does not authorize CLI argument parsing changes.

This contract does not authorize CLI command routing changes.

This contract does not authorize write-enabled export.

This contract does not authorize directory creation.

This contract does not authorize artifact creation on disk.

This contract does not authorize real file writing.

This contract does not authorize media scanning.

This contract does not authorize real media decoding.

This contract does not authorize ffprobe execution.

This contract does not authorize FFmpeg execution.

This contract does not authorize subprocess execution.

This contract does not authorize audio extraction.

This contract does not authorize sync.

This contract does not authorize transcription.

This contract does not authorize subtitle generation.

This contract does not authorize timeline export.

This contract does not authorize network access.

This contract does not authorize SaaS integration.

This contract does not authorize database changes.

This contract does not authorize backend changes.

This contract does not authorize frontend changes.

This contract does not authorize installer work.

This contract does not authorize public demo work.

This contract does not authorize client-facing demo work.

This contract does not authorize production use.

## Contract rejection conditions

This contract must fail if it authorizes:

- CLI integration code.
- CLI argument parsing changes.
- CLI command routing changes.
- write-enabled export.
- directory creation.
- artifact creation on disk.
- real file writing.
- media scanning.
- real media decoding.
- ffprobe execution.
- FFmpeg execution.
- subprocess execution.
- audio extraction.
- sync.
- transcription.
- subtitle generation.
- timeline export.
- network access.
- SaaS integration.
- database changes.
- backend changes.
- frontend changes.
- installer work.
- public demo behavior.
- client-facing demo behavior.
- production behavior.

## Contract decision

The future CLI dry-run integration boundary is defined.

The controlled dry-run bridge remains the only accepted future integration target.

The project is ready for a future doc/test-only CLI dry-run integration contract QA gate.

The project is not ready for CLI dry-run integration code.

The project is not ready for CLI argument parsing changes.

The project is not ready for CLI command routing changes.

The project is not ready for write-enabled export behavior.

The project is not ready for directory creation.

The project is not ready for artifact creation on disk.

The project is not ready for real media execution.

The project is not ready for public, client-facing, or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.CONTRACT.QA.GATE.V1`

That next step must remain doc/test-only.
