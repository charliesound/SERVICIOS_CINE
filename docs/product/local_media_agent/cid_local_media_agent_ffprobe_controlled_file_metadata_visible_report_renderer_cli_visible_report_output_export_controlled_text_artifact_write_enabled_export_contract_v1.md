# CID Local Media Agent — FFprobe controlled file metadata visible report renderer CLI visible report output export controlled text artifact write-enabled export contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.V1`

## Contract result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CONTRACT_PASS_READY_FOR_QA_GATE`

## Contract date

2026-06-29

## Contract type

This is a doc/test-only contract.

This contract defines a future controlled write-enabled export boundary.

This contract does not add implementation code.

This contract does not modify CLI argument parsing.

This contract does not modify command routing.

This contract does not modify the controlled dry-run bridge.

This contract does not perform write-enabled export.

This contract does not create directories.

This contract does not create artifacts on disk.

## Previous stable state

Previous stable commit:

`90220f5ed763e8fc93a5760d978d545752f8761b`

Previous stable tag:

`cid-dev-stable-local-media-agent-cli-dry-run-next-scope-planning-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.NEXT_SCOPE.PLANNING.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_NEXT_SCOPE_PLANNING_PASS_CLOSED`

Previous product decision:

`PATH_B_WRITE_ENABLED_EXPORT_CONTRACT_FIRST`

## Target tag

`cid-dev-stable-local-media-agent-write-enabled-export-contract-v1-20260629`

## Files in scope

Only these files are in scope for this contract:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_contract_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_contract.py`

No other files are in scope.

## Product intent

The product intent is to prepare the first future controlled write-enabled export path.

The first future controlled write-enabled export path must export one controlled visible report text artifact.

The first future controlled write-enabled export path must remain local-only.

The first future controlled write-enabled export path must remain fixture-owned or test-owned.

The first future controlled write-enabled export path must remain isolated from real user media.

The first future controlled write-enabled export path must remain isolated from client-facing behavior.

The first future controlled write-enabled export path must remain isolated from public demo and production behavior.

## Future artifact type

The future artifact type is:

`controlled_visible_report_text`

The future artifact must be plain UTF-8 text.

The future artifact must be deterministic for the same input.

The future artifact must be generated only from controlled visible report text already present in memory.

The future artifact must not require media files.

The future artifact must not require scanner execution.

The future artifact must not require ffprobe execution.

The future artifact must not require FFmpeg execution.

The future artifact must not require external process execution.

The future artifact must not require network access.

The future artifact must not require SaaS or database access.

## Future controlled output root contract

The future write-enabled export must require an explicit controlled output root.

The controlled output root must be provided by a test fixture or equivalent controlled caller.

The controlled output root must not be inferred from the current working directory.

The controlled output root must not be inferred from user home.

The controlled output root must not be inferred from environment variables.

The controlled output root must not be inferred from input media paths.

The controlled output root must not be inferred from SaaS state.

The controlled output root must be resolved before write.

The controlled output root must exist before write unless a future explicit directory-creation contract authorizes otherwise.

This contract does not authorize directory creation.

## Future filename contract

The future write-enabled export must use deterministic filenames.

The first future allowed filename is:

`controlled_visible_report.controlled.txt`

Allowed filename characters must be limited to:

`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-`

The filename must not contain path separators.

The filename must not contain parent traversal.

The filename must not begin with a dot.

The filename must not be empty.

The filename must not be generated from unsanitized input.

The filename must not be generated from real media names.

The filename must not be generated from user-provided folder names.

## Future extension contract

The first future allowed extension is:

`.controlled.txt`

The future write-enabled export must reject unsupported extensions.

The future write-enabled export must reject extensionless names.

The future write-enabled export must reject compound unsafe names.

The future write-enabled export must reject names that only appear to end with the allowed extension after traversal or separator manipulation.

## Future path boundary contract

The future write-enabled export must resolve the controlled output root.

The future write-enabled export must resolve the candidate artifact path.

The future write-enabled export must verify that the candidate artifact path remains inside the controlled output root.

The future write-enabled export must reject parent traversal.

The future write-enabled export must reject absolute unsafe paths.

The future write-enabled export must reject home-relative paths.

The future write-enabled export must reject environment-derived paths.

The future write-enabled export must reject symlink boundary ambiguity unless a future explicit symlink policy is defined.

The future write-enabled export must reject path boundary ambiguity.

## Future overwrite contract

The future write-enabled export must reject overwrite by default.

The future write-enabled export must not truncate an existing file.

The future write-enabled export must not append to an existing file.

The future write-enabled export must not replace an existing file.

The future write-enabled export must not support overwrite flags in the first implementation.

The future write-enabled export must report an explicit failure if the target artifact already exists.

## Future content contract

The future write-enabled export must accept controlled visible report text already present in memory.

The future write-enabled export must reject empty content.

The future write-enabled export must reject binary content.

The future write-enabled export must encode text as UTF-8.

The future write-enabled export must compute content hash before write.

The future write-enabled export must compute byte count before write.

The future write-enabled export must write exactly the intended bytes.

The future write-enabled export must verify content hash after write.

The future write-enabled export must verify byte count after write.

The future write-enabled export must fail closed if verification fails.

## Future result contract

The future write-enabled export result must include:

- phase.
- contract version.
- artifact type.
- artifact format.
- controlled output root.
- artifact path.
- filename.
- extension.
- write_requested.
- write_performed.
- artifact_created_on_disk.
- bytes_intended.
- bytes_written.
- content_sha256_before_write.
- content_sha256_after_write.
- path_boundary.
- overwrite_policy.
- verification_status.
- cleanup_expectation.
- safety_flags.
- warnings.
- errors.

## Future safety flags contract

The future safety flags must include:

- real_media_access_performed.
- scanner_execution_performed.
- ffprobe_execution_performed.
- ffmpeg_execution_performed.
- external_process_execution_performed.
- network_access_performed.
- saas_or_database_access_performed.
- directory_creation_performed.
- file_write_performed.
- artifact_created_on_disk.
- overwrite_performed.
- path_boundary_violation_detected.

The future accepted result may set `file_write_performed=True` only for the single controlled artifact write.

The future accepted result may set `artifact_created_on_disk=True` only for the single controlled artifact write.

The future accepted result must keep every other operational safety flag false.

## Future failure contract

The future write-enabled export must fail closed when:

- controlled output root is missing.
- controlled output root does not exist.
- output root is not controlled.
- output root is ambiguous.
- filename is missing.
- filename is unsupported.
- filename contains separators.
- filename contains parent traversal.
- filename begins with a dot.
- extension is unsupported.
- candidate path escapes controlled output root.
- candidate path is absolute unsafe.
- candidate path is home-relative.
- candidate path is environment-derived.
- target artifact already exists.
- content is empty.
- content cannot be encoded as UTF-8.
- bytes written differ from bytes intended.
- content hash after write differs from content hash before write.
- post-write verification fails.
- unexpected warnings appear.
- any prohibited operation is attempted.

## Future rollback and cleanup contract

The first future write-enabled export implementation must use fixture-owned output only.

The first future write-enabled export implementation must keep cleanup under test ownership.

The first future write-enabled export implementation must not delete arbitrary user files.

The first future write-enabled export implementation must not clean outside the controlled output root.

The first future write-enabled export implementation must not remove parent directories.

The first future write-enabled export implementation must report cleanup expectations instead of performing broad cleanup.

If a partial artifact is produced during a failed controlled write, future implementation readiness must define whether the artifact is removed or preserved for forensic inspection.

This contract does not authorize cleanup implementation.

## Future CLI boundary

The existing controlled dry-run CLI must remain dry-run-only until a future explicit implementation gate is closed.

A future write-enabled CLI must not reuse `--dry-run` semantics to perform writing.

A future write-enabled CLI must use a distinct explicit write authorization mechanism.

A future write-enabled CLI must require controlled output root.

A future write-enabled CLI must require deterministic filename or controlled default filename.

A future write-enabled CLI must not accept arbitrary output paths.

A future write-enabled CLI must not accept real media paths.

A future write-enabled CLI must not accept scanner execution flags.

A future write-enabled CLI must not accept ffprobe execution flags.

A future write-enabled CLI must not accept FFmpeg execution flags.

A future write-enabled CLI must not accept network flags.

A future write-enabled CLI must not accept production flags.

## Future implementation readiness requirements

Before implementation, a readiness gate must verify:

- exact module boundaries.
- exact function name.
- exact inputs.
- exact outputs.
- exact failure modes.
- exact allowed filesystem operation.
- exact prohibited filesystem operations.
- exact fixture-owned output policy.
- exact no-overwrite policy.
- exact post-write verification policy.
- exact test coverage.
- exact guard commands.
- exact rollback expectations.
- exact non-authorization of real media, scanner, ffprobe, FFmpeg, external process, network, SaaS, database, backend, frontend, installer, client demo, public demo, and production behavior.

## Current dry-run chain preservation

The existing controlled dry-run chain remains accepted.

The existing controlled dry-run CLI remains dry-run-only.

The existing controlled dry-run bridge remains dry-run-only.

The existing controlled smoke execution remains accepted.

The existing controlled smoke execution QA gate remains accepted and closed.

The existing next-scope planning remains accepted and closed.

This contract does not weaken any previous dry-run safety boundary.

## Rejection conditions for this contract

This contract must fail if it:

- adds implementation code.
- modifies CLI argument parsing.
- modifies command routing.
- modifies the controlled dry-run bridge.
- authorizes immediate write-enabled implementation.
- authorizes directory creation now.
- authorizes artifact creation on disk now.
- authorizes real file writing now.
- authorizes real media access.
- authorizes scanner execution.
- authorizes ffprobe execution.
- authorizes FFmpeg execution.
- authorizes external process execution.
- authorizes network access.
- authorizes SaaS integration.
- authorizes database changes.
- authorizes backend changes.
- authorizes frontend changes.
- authorizes installer work.
- authorizes client-facing demo.
- authorizes public demo.
- authorizes production use.
- omits controlled output root boundaries.
- omits filename boundaries.
- omits extension boundaries.
- omits path boundary checks.
- omits no-overwrite policy.
- omits content hash verification.
- omits byte count verification.
- omits failure behavior.
- omits fixture-owned output policy.
- skips implementation readiness.

## Explicit non-authorization

This contract does not authorize write-enabled export implementation.

This contract does not authorize directory creation.

This contract does not authorize artifact creation on disk now.

This contract does not authorize real file writing now.

This contract does not authorize media scanning.

This contract does not authorize real media decoding.

This contract does not authorize ffprobe execution.

This contract does not authorize FFmpeg execution.

This contract does not authorize external process execution.

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

## Contract decision

The controlled write-enabled export contract is accepted as a future boundary.

The current project remains dry-run-only.

The current project remains not ready for write-enabled implementation.

The current project remains not ready for directory creation.

The current project remains not ready for artifact creation on disk.

The current project remains not ready for real media execution.

The current project remains not ready for public, client-facing, or production use.

The next phase must be a contract QA gate.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.QA.GATE.V1`

That next step must remain doc/test-only.
