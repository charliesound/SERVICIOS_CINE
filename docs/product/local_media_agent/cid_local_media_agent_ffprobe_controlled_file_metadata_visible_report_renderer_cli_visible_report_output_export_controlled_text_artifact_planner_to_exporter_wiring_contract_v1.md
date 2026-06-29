# CID Local Media Agent — FFprobe controlled file metadata visible report renderer CLI visible report output export controlled text artifact planner to exporter wiring contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CONTRACT.V1`

## Contract result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CONTRACT_PASS_READY_FOR_QA_GATE`

## Contract date

2026-06-29

## Contract type

This is a doc/test-only contract.

This contract defines the minimum acceptable design for a future planner-to-exporter wiring implementation.

This contract does not implement planner-to-exporter wiring.

This contract does not modify planner runtime code.

This contract does not modify exporter runtime code.

This contract does not authorize write-enabled behavior.

## Previous stable state

Previous stable commit:

`ee53dcc8c1fd1aac98a58878d95b4478f89937dc`

Previous stable tag:

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-export-controlled-text-artifact-planner-to-exporter-wiring-readiness-gate-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.READINESS.GATE.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_READINESS_GATE_PASS_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-export-controlled-text-artifact-planner-to-exporter-wiring-contract-v1-20260629`

## Files in scope

Only these files are in scope for this contract phase:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_contract_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_contract.py`

No other files are in scope.

## Existing planner boundary

The existing controlled export path planner remains a pure planning component.

The planner validates the controlled export root.

The planner validates the suggested controlled visible report filename.

The planner requires the suffix `.controlled_visible_report.txt`.

The planner returns a planned controlled text artifact path descriptor.

The planner returns `write_performed=False`.

The planner returns `artifact_created_on_disk=False`.

The planner does not write files.

The planner does not create directories.

The planner does not create artifacts on disk.

The planner does not execute media tooling.

The planner does not access the network.

The planner does not touch SaaS, database, backend, frontend, installer, or client-facing code.

## Contracted future wiring model

A future implementation may only be considered if it follows this model:

1. caller prepares controlled visible report text.
2. caller prepares a controlled export root.
3. caller prepares a controlled descriptor containing `suggested_filename`.
4. planner validates the root and filename.
5. planner returns a controlled planner result.
6. exporter receives the planner result as an input.
7. exporter validates that the planner result is safe.
8. exporter uses the planner result as the only source of the planned artifact path.
9. exporter reports hash and write status deterministically.
10. exporter returns a visible export result without broadening scope.

The exporter must not silently recompute path policy.

The exporter must not accept arbitrary caller-provided output paths.

The exporter must not bypass planner safety decisions.

## Contracted future input schema

A future planner-to-exporter wiring implementation must accept an explicit structured input equivalent to:

- `visible_report_text`: controlled text content intended for a visible report artifact.
- `controlled_export_root`: controlled export root already subject to planner policy.
- `controlled_descriptor`: descriptor containing a controlled suggested filename.
- `planner_result`: controlled planner result returned by the planner.
- `dry_run`: boolean mode flag.
- `write_requested`: boolean intent flag.
- `artifact_format`: controlled artifact format.
- `caller_context`: non-sensitive local caller context.

The input must not include arbitrary output paths.

The input must not include raw media file content.

The input must not include secrets.

The input must not include network locations.

The input must not include SaaS tenant data.

The input must not include database identifiers.

## Contracted planner result schema

The future exporter-facing planner result must include:

- `controlled_export_root`.
- `suggested_filename`.
- `planned_artifact_path`.
- `artifact_format`.
- `content_sha256`.
- `write_performed`.
- `artifact_created_on_disk`.
- `path_boundary`.
- `safety_flags`.

The exporter must reject planner results that omit required fields.

The exporter must reject planner results with unsafe path boundaries.

The exporter must reject planner results with unsafe safety flags.

The exporter must reject planner results with a filename that does not end in `.controlled_visible_report.txt`.

The exporter must reject planner results that claim a write was already performed during planning.

The exporter must reject planner results that claim an artifact was already created during planning.

## Contracted future output schema

A future wiring result must include:

- `planned_artifact_path`.
- `artifact_format`.
- `content_sha256`.
- `write_requested`.
- `write_performed`.
- `artifact_created_on_disk`.
- `path_boundary`.
- `safety_flags`.
- `exporter_decision`.
- `human_visible_summary`.

The output must distinguish planning from writing.

The output must distinguish write intent from write execution.

The output must distinguish artifact path planning from artifact creation on disk.

## Contracted dry-run behavior

Dry-run mode is the only behavior allowed by this contract.

In dry-run mode, the future exporter must not write files.

In dry-run mode, the future exporter must not create directories.

In dry-run mode, the future exporter must not create artifacts on disk.

In dry-run mode, the future exporter must return `write_performed=False`.

In dry-run mode, the future exporter must return `artifact_created_on_disk=False`.

In dry-run mode, the future exporter must preserve the planned artifact path for human review.

## Write behavior

Write-enabled behavior is not authorized by this contract.

A later separate contract must exist before write-enabled behavior can be considered.

A later separate QA gate must exist before write-enabled behavior can be considered.

A later separate implementation gate must exist before write-enabled behavior can be implemented.

## Failure modes

A future implementation must fail closed for:

- missing planner result.
- malformed planner result.
- unsafe path boundary.
- unsafe safety flags.
- wrong filename suffix.
- empty visible report text.
- empty controlled export root.
- empty suggested filename.
- traversal in filename.
- path separators in filename.
- hidden filename.
- absolute output path provided by caller.
- write requested during dry-run.
- artifact already marked as created before exporter decision.

Failure results must not write files.

Failure results must not create directories.

Failure results must not create artifacts on disk.

Failure results must preserve a human-readable reason.

## CLI-visible contract

A future CLI-visible output may report:

- controlled export root.
- suggested filename.
- planned artifact path.
- artifact format.
- content hash.
- dry-run mode.
- write requested.
- write performed.
- artifact created on disk.
- safety decision.

A future CLI-visible output must not expose secrets.

A future CLI-visible output must not expose raw media content.

A future CLI-visible output must not imply that an artifact exists when no write occurred.

## Regression expectations

Any future implementation must preserve existing planner tests.

Any future implementation must preserve existing closure review tests.

Any future implementation must preserve this contract test.

Any future implementation must add implementation-specific tests before runtime changes are accepted.

Any future implementation must keep WSL guard passing.

Any future implementation must keep the database regression guard passing.

## Explicit non-authorization

This contract does not authorize connecting the planner to the exporter.

This contract does not authorize changing the planner module.

This contract does not authorize changing exporter runtime code.

This contract does not authorize path resolver expansion.

This contract does not authorize file writing.

This contract does not authorize directory creation.

This contract does not authorize artifact generation on disk.

This contract does not authorize real media usage.

This contract does not authorize arbitrary folder scanning.

This contract does not authorize scanner execution.

This contract does not authorize ffprobe execution.

This contract does not authorize FFmpeg execution.

This contract does not authorize child process execution.

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

The planner-to-exporter wiring design is defined enough for a future QA gate.

The project is not ready for planner-to-exporter runtime implementation.

The project is not ready for write-enabled export behavior.

The project is not ready for real media execution.

The project is not ready for client-facing or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CONTRACT.QA.GATE.V1`

That next step must remain doc/test-only.
