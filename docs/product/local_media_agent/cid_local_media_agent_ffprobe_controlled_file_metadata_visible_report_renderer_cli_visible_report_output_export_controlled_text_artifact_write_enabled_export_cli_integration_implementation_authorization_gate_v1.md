# CID Local Media Agent — write-enabled export CLI integration implementation authorization gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.IMPLEMENTATION.AUTHORIZATION.GATE.V1`

## Authorization gate result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_IMPLEMENTATION_PHASE`

## Authorization gate date

2026-06-29

## Authorization gate type

This is a doc/test-only authorization gate.

This authorization gate decides whether a later controlled implementation phase may be prepared.

This authorization gate does not implement CLI code.

This authorization gate does not create the future isolated CLI module.

This authorization gate does not add command-line write flags to the current dry-run CLI.

This authorization gate does not add output path flags to the current dry-run CLI.

This authorization gate does not add overwrite flags.

This authorization gate does not connect `export_controlled_visible_report_text_artifact` to current command execution.

This authorization gate does not modify the current dry-run CLI.

This authorization gate does not modify the current dry-run bridge.

This authorization gate does not write artifacts from the command line.

This authorization gate does not authorize client-facing usage.

This authorization gate does not authorize production usage.

## Previous stable state

Previous stable commit:

`8bf095db319424f6d3c8cdece1d9f938dbfbb7e0`

Previous stable tag:

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-readiness-gate-v2-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V2`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_READINESS_GATE_V2_PASS_READY_FOR_IMPLEMENTATION_AUTHORIZATION_GATE_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-authorization-gate-v1-20260629`

## Files in scope

Only these files are in scope for this authorization gate:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_authorization_gate_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_authorization_gate.py`

No other files are in scope.

## Artifacts under authorization review

CLI integration implementation readiness gate v2 document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.md`

CLI integration implementation readiness gate v2 test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.py`

CLI integration implementation contract QA gate closure review document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_closure_review_v1.md`

CLI integration implementation contract QA gate document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_v1.md`

CLI integration implementation contract document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_v1.md`

Controlled write-enabled primitive:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py`

Current dry-run CLI:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py`

Current dry-run bridge:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py`

Future isolated CLI module reserved by contract:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`

## Previous validation evidence accepted

The implementation readiness gate v2 was accepted because the recorded validation included:

- exact staged files check passed.
- staged diff check passed.
- restricted database word check passed.
- target CLI integration implementation readiness gate V2 test passed with 158 checks.
- previous CLI integration implementation contract QA closure review test passed with 175 checks.
- previous CLI integration implementation contract QA gate test passed with 243 checks.
- previous CLI integration implementation contract test passed with 235 checks.
- previous controlled implementation test passed with 33 checks.
- WSL guard passed.
- database regression guard passed.
- target readiness gate V2 tag was absent locally before tagging.
- target readiness gate V2 tag was absent remotely before tagging.
- commit completed.
- local tag completed.
- push main completed.
- push tag completed.
- post-push verification completed.
- final target CLI integration implementation readiness gate V2 test passed with 158 checks.
- final CLI integration implementation contract QA closure review test passed with 175 checks.
- final CLI integration implementation contract QA gate test passed with 243 checks.
- final CLI integration implementation contract test passed with 235 checks.
- final CLI integration implementation readiness gate V1 test passed with 179 checks.
- final CLI integration contract QA closure review test passed with 132 checks.
- final controlled implementation QA gate test passed with 183 checks.
- final controlled implementation test passed with 33 checks.
- final dry-run CLI forbidden marker check passed.
- final write-enabled implementation safety check passed.
- working tree was clean after post-push verification.

## Authorization acceptance criteria

This authorization gate may pass only if all criteria remain true:

- the implementation readiness gate v2 is closed.
- the implementation contract QA gate closure review is closed.
- the implementation contract QA gate is closed.
- the implementation contract is accepted.
- this authorization gate remains doc/test-only.
- the future isolated CLI module has not been created.
- no CLI implementation has been added.
- no command-line write flags have been added to the current dry-run CLI.
- no output path flags have been added to the current dry-run CLI.
- no overwrite flags have been added.
- the current dry-run CLI remains dry-run-only.
- the current dry-run bridge remains dry-run-only.
- the accepted write-enabled primitive remains isolated from current command execution.
- the future isolated CLI module name remains reserved.
- the future command identity remains reserved.
- the future allowed argument set remains constrained.
- the future forbidden argument set remains constrained.
- future implementation remains limited to fixture-owned controlled output roots.
- future implementation preserves exact write authorization.
- future implementation preserves no-overwrite behavior.
- future implementation preserves no-directory-creation behavior.
- future implementation preserves single-artifact behavior.
- future implementation preserves byte count verification.
- future implementation preserves SHA256 verification.
- future implementation preserves conservative safety flags.
- future implementation preserves fail-closed behavior.

## Narrow implementation authorization decision

A later controlled implementation phase may be prepared.

That later implementation phase may create exactly one new runtime module:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`

That later implementation phase may create exactly one new implementation test file:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py`

That later implementation phase may import `export_controlled_visible_report_text_artifact` only from the accepted controlled write-enabled primitive.

That later implementation phase may build an isolated parser only in the new isolated module.

That later implementation phase may expose an internal command identity only as data or parser metadata:

`cid-local-media-agent-visible-report-write-enabled-export`

That later implementation phase may add an internal `main` function only inside the new isolated module.

That later implementation phase may add an internal `run` or `execute` helper only inside the new isolated module.

That later implementation phase may return deterministic result data.

That later implementation phase may return exit code `0` for valid dry-run.

That later implementation phase may return exit code `0` for verified fixture-owned controlled write.

That later implementation phase must return non-zero exit code for rejected input.

## Authorized later implementation file boundary

The later controlled implementation phase may modify only:

1. `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py`

No other runtime, test, docs, config, packaging, backend, frontend, database, installer, CI, or deployment files are authorized by this gate.

The current dry-run CLI remains out of implementation scope.

The current dry-run bridge remains out of implementation scope.

The accepted controlled write-enabled primitive remains out of modification scope.

## Authorized later parser behavior

The later isolated CLI parser may support only these options:

- `--visible-report-text`
- `--controlled-output-root`
- `--write-authorization`
- `--result-json`
- `--dry-run`

The later isolated CLI parser must reject unsafe aliases, including:

- `--output`
- `--output-path`
- `--artifact-path`
- `--overwrite`
- `--force`
- `--create-dir`
- `--mkdir`
- `--production`
- `--client`
- `--public-demo`
- `--ffprobe`
- `--ffmpeg`
- `--network`
- `--database`

The later isolated CLI parser must reject unknown arguments.

The later isolated CLI parser must not be registered as a package entry point.

The later isolated CLI parser must not modify the current dry-run CLI.

## Authorized later dry-run behavior

The later isolated CLI dry-run mode may:

- parse allowed arguments.
- validate that dry-run mode was requested.
- return deterministic result data.
- report `dry_run_requested` as true.
- report `write_requested` as false.
- report `write_performed` as false.
- report `artifact_created_on_disk` as false.
- report `verification_status` as `DRY_RUN_ONLY`.
- return exit code `0`.

The later isolated CLI dry-run mode must not:

- create artifacts.
- create directories.
- overwrite files.
- call the controlled write-enabled primitive.
- access real media.
- execute scanner.
- execute ffprobe.
- execute FFmpeg.
- execute external processes.
- use network access.
- use SaaS or database integration.

## Authorized later controlled write behavior

The later isolated CLI controlled write mode may:

- require visible report text.
- require controlled output root.
- require exact write authorization.
- require `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`.
- call `export_controlled_visible_report_text_artifact`.
- write only `controlled_visible_report.controlled.txt`.
- write only under fixture-owned controlled output roots.
- preserve no-overwrite behavior.
- preserve no-directory-creation behavior.
- preserve UTF-8 byte count verification.
- preserve SHA256 verification.
- return deterministic result data.
- return exit code `0` only when verification status is `VERIFIED`.

The later isolated CLI controlled write mode must reject:

- missing visible report text.
- empty visible report text.
- missing controlled output root.
- uncontrolled output root.
- current working directory as output root.
- repository root as output root.
- existing artifact path.
- unsupported filename.
- path traversal.
- missing write authorization.
- dry-run authorization.
- unknown write authorization.
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

## Required later implementation test matrix

The later controlled implementation phase must include tests for:

- isolated CLI module exists.
- isolated CLI parser construction.
- command identity.
- allowed argument set.
- forbidden unsafe alias rejection.
- unknown argument rejection.
- dry-run mode without artifact creation.
- dry-run mode does not call the controlled write-enabled primitive.
- missing visible report text rejection.
- empty visible report text rejection.
- missing controlled output root rejection.
- missing write authorization rejection.
- dry-run authorization rejection.
- unknown authorization rejection.
- repository root rejection.
- current working directory rejection.
- existing artifact rejection.
- no directory creation.
- no overwrite.
- deterministic JSON result fields.
- non-zero exit for rejected inputs.
- zero exit for valid dry-run.
- zero exit for verified fixture-owned controlled write.
- controlled write creates exactly one artifact.
- controlled write uses filename `controlled_visible_report.controlled.txt`.
- controlled write verifies byte count.
- controlled write verifies SHA256.
- current dry-run CLI remains unchanged.
- current dry-run bridge remains unchanged.
- current dry-run CLI does not import the new isolated CLI module.
- current dry-run bridge does not import the new isolated CLI module.
- isolated CLI does not execute scanner.
- isolated CLI does not execute ffprobe.
- isolated CLI does not execute FFmpeg.
- isolated CLI does not use external process execution.
- isolated CLI does not use network.
- isolated CLI does not use SaaS or database integration.

## Explicit non-authorization retained

This authorization gate does not authorize implementation in this phase.

This authorization gate does not authorize modifying the current dry-run CLI.

This authorization gate does not authorize modifying the current dry-run bridge.

This authorization gate does not authorize modifying the accepted controlled write-enabled primitive.

This authorization gate does not authorize package entry points.

This authorization gate does not authorize installer work.

This authorization gate does not authorize client-facing demo work.

This authorization gate does not authorize public demo work.

This authorization gate does not authorize production use.

This authorization gate does not authorize writing outside fixture-owned roots.

This authorization gate does not authorize directory creation.

This authorization gate does not authorize overwrite.

This authorization gate does not authorize multiple artifacts.

This authorization gate does not authorize arbitrary cleanup.

This authorization gate does not authorize real media access.

This authorization gate does not authorize scanner execution.

This authorization gate does not authorize ffprobe execution.

This authorization gate does not authorize FFmpeg execution.

This authorization gate does not authorize external process execution.

This authorization gate does not authorize network access.

This authorization gate does not authorize SaaS integration.

This authorization gate does not authorize database integration.

This authorization gate does not authorize backend changes.

This authorization gate does not authorize frontend changes.

## Authorization gate decision

The write-enabled export CLI integration implementation authorization gate passes.

A later controlled implementation phase may be prepared.

The later controlled implementation phase is authorized only within the file boundary, parser boundary, behavior boundary, and test boundary defined here.

The current project remains dry-run-only from the current command line.

The current project remains not ready for client-facing or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1`

That next step may implement only the new isolated CLI module and its implementation test.

That next step must not modify the current dry-run CLI.

That next step must not modify the current dry-run bridge.

That next step must not modify the accepted controlled write-enabled primitive.

That next step must not add package entry points.

That next step must not add installer work.

That next step must not add client-facing or production usage.

That next step must not touch backend, frontend, database, SaaS, deployment, or external process execution.
