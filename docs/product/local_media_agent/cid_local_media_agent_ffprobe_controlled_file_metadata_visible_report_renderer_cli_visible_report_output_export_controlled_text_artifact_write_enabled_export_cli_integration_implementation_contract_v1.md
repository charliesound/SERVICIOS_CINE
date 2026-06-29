# CID Local Media Agent — write-enabled export CLI integration implementation contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.IMPLEMENTATION.CONTRACT.V1`

## Contract result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_CONTRACT_DEFINED`

## Contract date

2026-06-29

## Contract type

This is a doc/test-only controlled implementation contract.

This contract defines a future isolated write-enabled CLI implementation boundary.

This contract does not implement CLI code.

This contract does not add command-line write flags.

This contract does not add output path flags.

This contract does not add overwrite flags.

This contract does not connect `export_controlled_visible_report_text_artifact` to current command execution.

This contract does not modify the current dry-run CLI.

This contract does not modify the current dry-run bridge.

This contract does not write artifacts from the command line.

This contract does not authorize client-facing usage.

This contract does not authorize production usage.

## Previous stable state

Previous stable commit:

`5843ee37f497d334c7cf5546ec1a46ac9bac7ec4`

Previous stable tag:

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-readiness-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_CONTROLLED_IMPLEMENTATION_CONTRACT_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-contract-v1-20260629`

## Files in scope

Only these files are in scope for this contract:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract.py`

No other files are in scope.

## Artifacts under contract review

CLI integration implementation readiness gate document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v1.md`

CLI integration implementation readiness gate test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate.py`

CLI integration contract QA gate closure review document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_closure_review_v1.md`

CLI integration contract document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract_v1.md`

Controlled write-enabled primitive:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py`

Current dry-run CLI:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py`

Current dry-run bridge:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py`

## Previous validation evidence accepted

The CLI integration implementation readiness gate was accepted because the recorded validation included:

- exact staged files check passed.
- staged diff check passed.
- restricted database word check passed.
- target CLI integration implementation readiness gate test passed with 179 checks.
- previous CLI integration contract QA closure review test passed with 132 checks.
- previous CLI integration contract QA gate test passed with 173 checks.
- previous CLI integration contract test passed with 189 checks.
- previous controlled implementation test passed with 33 checks.
- WSL guard passed.
- database regression guard passed.
- target implementation readiness tag was absent locally before tagging.
- target implementation readiness tag was absent remotely before tagging.
- commit completed.
- local tag completed.
- push main completed.
- push tag completed.
- post-push verification completed.
- final target CLI integration implementation readiness gate test passed with 179 checks.
- final CLI integration contract QA closure review test passed with 132 checks.
- final CLI integration contract QA gate test passed with 173 checks.
- final CLI integration contract test passed with 189 checks.
- final CLI integration readiness test passed with 113 checks.
- final controlled implementation QA gate test passed with 183 checks.
- final controlled implementation test passed with 33 checks.
- final dry-run CLI forbidden marker check passed.
- final write-enabled implementation safety check passed.
- working tree was clean after post-push verification.

## Implementation design selected for future phase

A future controlled implementation phase may add a separate CLI module dedicated to controlled write-enabled export.

The separate CLI module name reserved for future implementation is:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`

The future implementation must not modify the current dry-run CLI.

The future implementation must not modify the current dry-run bridge.

The future implementation must not add write-enabled behavior to the current dry-run command.

The future implementation must keep dry-run and write-enabled command paths separate.

The future implementation must import the accepted primitive only from the new isolated write-enabled CLI module.

The future implementation must not import the accepted primitive from the current dry-run CLI module.

The future implementation must not import the accepted primitive from the current dry-run bridge module.

## Future command contract

The future isolated write-enabled CLI module may expose a parser with this controlled command identity:

`cid-local-media-agent-visible-report-write-enabled-export`

The future command may accept only these explicit arguments:

- `--visible-report-text`
- `--controlled-output-root`
- `--write-authorization`
- `--result-json`
- `--dry-run`

The future command must reject unknown arguments.

The future command must not accept `--output`.

The future command must not accept `--output-path`.

The future command must not accept `--artifact-path`.

The future command must not accept `--overwrite`.

The future command must not accept `--force`.

The future command must not accept `--create-dir`.

The future command must not accept `--mkdir`.

The future command must not accept `--production`.

The future command must not accept `--client`.

The future command must not accept `--public-demo`.

The future command must not accept `--ffprobe`.

The future command must not accept `--ffmpeg`.

The future command must not accept `--network`.

The future command must not accept `--database`.

## Future dry-run behavior for isolated write-enabled CLI

The future isolated write-enabled CLI may support `--dry-run`.

When `--dry-run` is used, the future isolated write-enabled CLI must not create an artifact.

When `--dry-run` is used, the future isolated write-enabled CLI must report:

- `dry_run_requested` as true.
- `write_requested` as false.
- `write_performed` as false.
- `artifact_created_on_disk` as false.
- `verification_status` as `DRY_RUN_ONLY`.

When `--dry-run` is not used, the future isolated write-enabled CLI may request controlled fixture-owned writing only if all required inputs are valid.

## Future write-enabled behavior for isolated CLI

The future isolated write-enabled CLI must require:

- visible report text.
- controlled output root.
- exact write authorization.
- explicit result JSON destination if result file output is later authorized by a separate contract.

The future isolated write-enabled CLI must use:

`CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`

The future isolated write-enabled CLI must call:

`export_controlled_visible_report_text_artifact`

The future isolated write-enabled CLI must preserve:

- fixture-owned root validation.
- single-artifact behavior.
- filename `controlled_visible_report.controlled.txt`.
- no-overwrite behavior.
- no directory creation behavior.
- UTF-8 byte count verification.
- SHA256 verification.
- deterministic result dictionary.
- conservative safety flags.
- fail-closed behavior.

## Future result JSON schema

The future isolated write-enabled CLI result must include:

- phase.
- cli_contract_version.
- command_name.
- module_name.
- mode.
- dry_run_requested.
- write_requested.
- write_performed.
- artifact_created_on_disk.
- controlled_output_root.
- artifact_path.
- filename.
- extension.
- write_authorization.
- bytes_intended.
- bytes_written.
- content_sha256_before_write.
- content_sha256_after_write.
- overwrite_policy.
- verification_status.
- safety_flags.
- warnings.
- errors.
- exit_code.

## Future exit code policy

The future isolated write-enabled CLI must return exit code `0` only when:

- dry-run completed without write; or
- controlled fixture-owned write completed and verification status is `VERIFIED`.

The future isolated write-enabled CLI must return non-zero exit code when:

- write authorization is missing.
- write authorization is dry-run-only.
- write authorization is unknown.
- visible report text is missing.
- controlled output root is missing.
- controlled output root is not controlled.
- controlled output root is the repository root.
- artifact already exists.
- unsupported filename is requested.
- path traversal is attempted.
- directory creation would be required.
- overwrite would be required.
- scanner execution is requested.
- ffprobe execution is requested.
- FFmpeg execution is requested.
- external process execution is requested.
- network access is requested.
- SaaS or database access is requested.
- client-facing or production mode is requested.

## Mandatory rejection cases for future implementation

The future isolated write-enabled CLI implementation must reject:

- missing write authorization.
- dry-run authorization.
- unknown write authorization.
- missing visible report text.
- empty visible report text.
- missing controlled output root.
- uncontrolled output root.
- current working directory as output root.
- repository root as output root.
- existing artifact path.
- unsupported filename.
- path traversal.
- overwrite request.
- directory creation request.
- production mode request.
- client-facing mode request.
- public demo mode request.
- real media access request.
- scanner execution request.
- ffprobe execution request.
- FFmpeg execution request.
- external process execution request.
- network request.
- SaaS integration request.
- database integration request.

## Mandatory compatibility checks for future implementation

The future implementation must include tests proving:

- the current dry-run CLI parser has no write-enabled options.
- the current dry-run CLI source does not import the write-enabled primitive.
- the current dry-run bridge source does not import the write-enabled primitive.
- the current dry-run bridge remains dry-run-only.
- the future isolated write-enabled CLI has its own parser.
- the future isolated write-enabled CLI rejects unknown arguments.
- the future isolated write-enabled CLI rejects unsafe output aliases.
- the future isolated write-enabled CLI supports dry-run without writing.
- the future isolated write-enabled CLI supports controlled fixture-owned write only with explicit authorization.
- the future isolated write-enabled CLI returns deterministic result data.
- the future isolated write-enabled CLI returns non-zero exit on rejected inputs.
- the accepted primitive still rejects dry-run authorization.
- the accepted primitive still rejects repository root output.
- the accepted primitive still rejects existing artifacts.
- the accepted primitive still performs no directory creation.
- the accepted primitive still performs no overwrite.
- the accepted primitive still performs no external process execution.
- the accepted primitive still performs no network access.
- the accepted primitive still performs no SaaS or database access.

## Explicit non-authorization

This contract does not authorize CLI implementation.

This contract does not authorize command-line write flags in the current dry-run CLI.

This contract does not authorize output path flags in the current dry-run CLI.

This contract does not authorize overwrite flags.

This contract does not authorize writing from current user-facing command execution.

This contract does not authorize writing outside fixture-owned roots.

This contract does not authorize directory creation.

This contract does not authorize overwrite.

This contract does not authorize multiple artifacts.

This contract does not authorize arbitrary cleanup.

This contract does not authorize real media access.

This contract does not authorize scanner execution.

This contract does not authorize ffprobe execution.

This contract does not authorize FFmpeg execution.

This contract does not authorize external process execution.

This contract does not authorize network access.

This contract does not authorize SaaS integration.

This contract does not authorize database integration.

This contract does not authorize backend changes.

This contract does not authorize frontend changes.

This contract does not authorize installer work.

This contract does not authorize client-facing demo work.

This contract does not authorize public demo work.

This contract does not authorize production use.

## Contract decision

The controlled implementation contract for isolated write-enabled CLI integration is defined.

A later controlled implementation QA gate may be prepared.

The current project remains dry-run-only from the current command line.

The current project remains not ready for write-enabled CLI execution.

The current project remains not ready for client-facing or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.IMPLEMENTATION.CONTRACT.QA.GATE.V1`

That next step must remain doc/test-only.

That next step must not implement CLI code.

That next step must not add CLI flags.

That next step must not connect the primitive to command execution.

That next step may only audit this controlled implementation contract.
