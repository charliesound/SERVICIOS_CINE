# CID Local Media Agent — write-enabled export CLI integration contract QA gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTRACT.QA.GATE.V1`

## QA gate result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_CONTRACT_QA_GATE_PASS`

## QA gate date

2026-06-29

## QA gate type

This is a doc/test-only QA gate.

This QA gate audits the write-enabled export CLI integration contract.

This QA gate does not implement the CLI integration.

This QA gate does not add command-line write flags.

This QA gate does not add output path flags.

This QA gate does not add overwrite flags.

This QA gate does not connect `export_controlled_visible_report_text_artifact` to current command execution.

This QA gate does not modify the current dry-run CLI.

This QA gate does not modify the current dry-run bridge.

This QA gate does not write artifacts from the command line.

This QA gate does not authorize client-facing usage.

This QA gate does not authorize production usage.

## Previous stable state

Previous stable commit:

`43322bb06aa6544fc4075a738d71186e83757b32`

Previous stable tag:

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTRACT.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_CONTRACT_DEFINED_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-qa-gate-v1-20260629`

## Files in scope

Only these files are in scope for this QA gate:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate.py`

No other files are in scope.

## Artifacts under QA

CLI integration contract document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract_v1.md`

CLI integration contract test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract.py`

CLI integration readiness document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate_v1.md`

Controlled write-enabled primitive:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py`

Current dry-run CLI:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py`

Current dry-run bridge:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py`

## Previous validation evidence accepted

The CLI integration contract was accepted because the recorded validation included:

- precheck was clean.
- previous CLI integration readiness tag was present.
- target CLI integration contract tag was absent locally before tagging.
- target CLI integration contract tag was absent remotely before tagging.
- exact staged files check passed.
- staged diff check passed.
- restricted database word check passed.
- target CLI integration contract test passed with 189 checks.
- previous CLI integration readiness test passed with 113 checks.
- previous controlled implementation QA closure review test passed with 110 checks.
- previous controlled implementation test passed with 33 checks.
- WSL guard passed.
- database regression guard passed.
- commit completed.
- local tag completed.
- push main completed.
- push tag completed.
- post-push verification completed.
- final target CLI integration contract test passed with 189 checks.
- final CLI integration readiness test passed with 113 checks.
- final controlled implementation QA closure review test passed with 110 checks.
- final controlled implementation QA gate test passed with 183 checks.
- final controlled implementation test passed with 33 checks.
- final dry-run CLI forbidden marker check passed.
- final write-enabled implementation safety check passed.
- working tree was clean after post-push verification.

## QA acceptance criteria

This QA gate accepts the CLI integration contract only if all criteria remain true:

- the contract is doc/test-only.
- the contract does not implement CLI integration.
- the contract does not add command-line write flags.
- the contract does not add output path flags.
- the contract does not add overwrite flags.
- the contract does not connect the write-enabled primitive to current command execution.
- the contract does not modify the current dry-run CLI.
- the contract does not modify the current dry-run bridge.
- the contract preserves current dry-run-only command behavior.
- the contract preserves current dry-run-only bridge behavior.
- the contract requires future CLI integration to use a separate explicit command path.
- the contract requires future CLI integration to require explicit write authorization.
- the contract requires future CLI integration to require explicit controlled output root.
- the contract requires future CLI integration to preserve fixture-owned root validation.
- the contract requires future CLI integration to preserve single-artifact behavior.
- the contract requires future CLI integration to preserve no-overwrite behavior.
- the contract requires future CLI integration to preserve byte count verification.
- the contract requires future CLI integration to preserve SHA256 verification.
- the contract requires future CLI integration to preserve deterministic result JSON.
- the contract requires future CLI integration to preserve conservative safety flags.
- the contract requires future CLI integration to fail closed on invalid input.
- the contract requires future CLI integration to keep dry-run and write-enabled results clearly separated.

## Accepted primitive under QA

The accepted primitive remains:

`export_controlled_visible_report_text_artifact`

The accepted authorization remains:

`CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`

The accepted artifact remains:

`controlled_visible_report.controlled.txt`

The accepted artifact policy remains:

`single fixture-owned controlled text artifact`

The accepted write policy remains:

`NO_OVERWRITE`

The accepted verification policy remains:

`UTF-8 bytes and SHA256 before and after write`

## Required future rejection cases under QA

The future CLI integration contract must reject:

- missing write authorization.
- dry-run authorization.
- unknown write authorization.
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
- scanner execution request.
- ffprobe execution request.
- FFmpeg execution request.
- network request.
- SaaS integration request.
- database integration request.

## Required future result JSON under QA

The future CLI integration contract must require result JSON including:

- phase.
- cli_contract_version.
- command_name.
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

## Required safety expectations under QA

The future CLI integration contract must keep these flags false unless a later explicit contract authorizes otherwise:

- real_media_access_performed.
- scanner_execution_performed.
- ffprobe_execution_performed.
- ffmpeg_execution_performed.
- external_process_execution_performed.
- network_access_performed.
- saas_or_database_access_performed.
- directory_creation_performed.
- overwrite_performed.
- production_execution_performed.
- client_facing_execution_performed.
- public_demo_execution_performed.

Only these flags may become true in the future controlled fixture-owned write-enabled CLI scenario:

- write_requested.
- write_performed.
- artifact_created_on_disk.
- file_write_performed.

## Explicit non-authorization

This QA gate does not authorize CLI implementation.

This QA gate does not authorize command-line write flags.

This QA gate does not authorize output path flags.

This QA gate does not authorize overwrite flags.

This QA gate does not authorize writing from user-facing command execution.

This QA gate does not authorize writing outside fixture-owned roots.

This QA gate does not authorize directory creation.

This QA gate does not authorize overwrite.

This QA gate does not authorize multiple artifacts.

This QA gate does not authorize arbitrary cleanup.

This QA gate does not authorize real media access.

This QA gate does not authorize scanner execution.

This QA gate does not authorize ffprobe execution.

This QA gate does not authorize FFmpeg execution.

This QA gate does not authorize external process execution.

This QA gate does not authorize network access.

This QA gate does not authorize SaaS integration.

This QA gate does not authorize database integration.

This QA gate does not authorize backend changes.

This QA gate does not authorize frontend changes.

This QA gate does not authorize installer work.

This QA gate does not authorize client-facing demo work.

This QA gate does not authorize public demo work.

This QA gate does not authorize production use.

## QA gate decision

The write-enabled export CLI integration contract is accepted by QA gate.

The current project remains dry-run-only from the command line.

The current project remains not ready for write-enabled CLI execution.

The current project remains not ready for client-facing or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1`

That next step must remain doc/test-only.

That next step must not add CLI flags.

That next step must not connect the primitive to command execution.

That next step may only close this QA gate.
