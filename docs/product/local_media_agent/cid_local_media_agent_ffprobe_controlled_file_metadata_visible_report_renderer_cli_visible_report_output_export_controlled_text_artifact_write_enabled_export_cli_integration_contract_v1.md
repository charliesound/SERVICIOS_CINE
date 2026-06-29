# CID Local Media Agent — write-enabled export CLI integration contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTRACT.V1`

## Contract result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_CONTRACT_DEFINED`

## Contract date

2026-06-29

## Contract type

This is a doc/test-only contract.

This contract defines a future write-enabled CLI integration boundary.

This contract does not implement the CLI integration.

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

`38dc82dc7f8c85303d3e8e57fa1b1e603cf0deb0`

Previous stable tag:

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-readiness-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.READINESS.GATE.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_READINESS_GATE_PASS_READY_FOR_CLI_INTEGRATION_CONTRACT_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-v1-20260629`

## Files in scope

Only these files are in scope for this contract:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_contract.py`

No other files are in scope.

## Artifacts under contract review

CLI integration readiness gate:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate_v1.md`

CLI integration readiness test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate.py`

Controlled write-enabled primitive:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py`

Current dry-run CLI:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py`

Current dry-run bridge:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py`

## Previous validation evidence accepted

The CLI integration readiness gate was accepted because the recorded validation included:

- precheck was clean.
- previous CLI integration readiness input tag was present.
- target CLI integration readiness tag was absent locally before tagging.
- target CLI integration readiness tag was absent remotely before tagging.
- exact staged files check passed.
- staged diff check passed.
- restricted database word check passed.
- target CLI integration readiness gate test passed with 113 checks.
- previous controlled implementation QA closure review test passed with 110 checks.
- previous controlled implementation QA gate test passed with 183 checks.
- previous controlled implementation test passed with 33 checks.
- WSL guard passed.
- database regression guard passed.
- commit completed.
- local tag completed.
- push main completed.
- push tag completed.
- post-push verification completed.
- final target CLI integration readiness gate test passed with 113 checks.
- final controlled implementation QA closure review test passed with 110 checks.
- final controlled implementation QA gate test passed with 183 checks.
- final controlled implementation test passed with 33 checks.
- final implementation readiness gate test passed with 322 checks.
- final dry-run CLI forbidden marker check passed.
- final write-enabled implementation safety check passed.
- working tree was clean after post-push verification.

## Accepted primitive

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

## Required future CLI integration shape

A future write-enabled CLI integration must use a separate explicit command path from the current dry-run command.

The current dry-run CLI must remain dry-run-only.

The current dry-run bridge must remain dry-run-only.

A future write-enabled CLI integration must not silently reuse dry-run authorization.

A future write-enabled CLI integration must require explicit write authorization.

A future write-enabled CLI integration must require an explicit controlled output root.

A future write-enabled CLI integration must preserve fixture-owned root validation until a later explicit contract authorizes another root policy.

A future write-enabled CLI integration must preserve single-artifact behavior.

A future write-enabled CLI integration must preserve no-overwrite behavior.

A future write-enabled CLI integration must preserve byte count verification.

A future write-enabled CLI integration must preserve SHA256 verification.

A future write-enabled CLI integration must preserve deterministic result JSON.

A future write-enabled CLI integration must preserve conservative safety flags.

A future write-enabled CLI integration must fail closed on invalid input.

A future write-enabled CLI integration must keep dry-run and write-enabled results clearly separated.

## Future command boundary

The future command boundary may be specified as either:

- a separate CLI module dedicated to controlled write-enabled export; or
- a separate subcommand isolated from the current dry-run command.

The future command boundary must not be added in this contract phase.

The future command boundary must be introduced only after a future implementation readiness gate.

The future command boundary must include tests proving that the current dry-run command remains unchanged.

## Future required CLI inputs

A future write-enabled CLI integration contract must define all required inputs explicitly:

- visible report text input source.
- controlled output root input.
- explicit write authorization input.
- artifact filename policy.
- dry-run/write-enabled mode separation.
- result JSON output policy.
- failure output policy.
- safety flags output policy.

No future write-enabled CLI integration may infer authorization from environment variables.

No future write-enabled CLI integration may infer output root from the current working directory.

No future write-enabled CLI integration may write to the repository root.

No future write-enabled CLI integration may write to user media folders unless a later explicit client-folder contract authorizes it.

## Future required rejection cases

A future write-enabled CLI integration contract must reject:

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

## Future required result JSON

A future write-enabled CLI integration contract must expose result JSON including:

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

## Future safety flag expectations

A future write-enabled CLI integration contract must keep these flags false unless a later explicit contract authorizes otherwise:

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

Only these flags may become true in the future controlled write-enabled fixture-owned CLI scenario:

- write_requested.
- write_performed.
- artifact_created_on_disk.
- file_write_performed.

## Required compatibility guarantees

The future CLI integration must remain compatible with:

- current dry-run CLI behavior.
- current dry-run bridge behavior.
- current controlled write-enabled primitive result shape.
- current no-overwrite behavior.
- current fixture-owned root restriction.
- current safety flag model.
- current fail-closed behavior.

## Explicit non-authorization

This contract does not authorize CLI implementation.

This contract does not authorize command-line write flags.

This contract does not authorize output path flags.

This contract does not authorize overwrite flags.

This contract does not authorize writing from user-facing command execution.

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

The future write-enabled CLI integration contract is defined.

The current project remains dry-run-only from the command line.

The current project remains not ready for write-enabled CLI execution.

The current project remains not ready for client-facing or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTRACT.QA.GATE.V1`

That next step must remain doc/test-only.

That next step must not add CLI flags.

That next step must not connect the primitive to command execution.

That next step may only audit this contract.
