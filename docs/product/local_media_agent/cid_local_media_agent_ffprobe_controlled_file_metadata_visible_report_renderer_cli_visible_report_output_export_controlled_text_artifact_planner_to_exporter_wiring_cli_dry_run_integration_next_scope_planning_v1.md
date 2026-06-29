# CID Local Media Agent — FFprobe controlled file metadata visible report renderer CLI visible report output export controlled text artifact planner to exporter wiring CLI dry-run integration next scope planning v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.NEXT_SCOPE.PLANNING.V1`

## Planning result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_NEXT_SCOPE_PLANNING_PASS_READY_FOR_WRITE_ENABLED_EXPORT_CONTRACT`

## Planning date

2026-06-29

## Planning type

This is a doc/test-only next-scope planning phase.

This planning phase selects the next product path after the controlled CLI dry-run smoke execution closure.

This planning phase does not add implementation code.

This planning phase does not modify CLI argument parsing.

This planning phase does not modify command routing.

This planning phase does not modify the controlled dry-run bridge.

This planning phase does not authorize write-enabled behavior.

## Previous stable state

Previous stable commit:

`90b7374cc5285b4eba9b9f6adcdff86e931ca9fb`

Previous stable tag:

`cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-qa-closure-review-v1-20260629`

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.QA.GATE.CLOSURE.REVIEW.V1`

Previous closed result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_SMOKE_EXECUTION_QA_GATE_CLOSURE_REVIEW_PASS_CLOSED`

## Target tag

`cid-dev-stable-local-media-agent-cli-dry-run-next-scope-planning-v1-20260629`

## Files in scope

Only these files are in scope for this planning phase:

1. `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning_v1.md`
2. `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning.py`

No other files are in scope.

## Product decision

The selected path is:

`PATH_B_WRITE_ENABLED_EXPORT_CONTRACT_FIRST`

Path B is selected because the controlled CLI dry-run chain is now closed through:

- controlled implementation.
- controlled implementation QA gate.
- controlled implementation QA gate closure review.
- controlled smoke execution.
- controlled smoke execution QA gate.
- controlled smoke execution QA gate closure review.

Path B is not an implementation authorization.

Path B only authorizes a future contract/readiness sequence for controlled write-enabled export.

Path B must remain conservative.

Path B must not skip directly into write-enabled code.

Path B must not skip directly into disk artifact creation.

Path B must not skip directly into real media.

Path B must not skip directly into client-facing use.

## Deferred path

Path A is deferred:

`PATH_A_QA_UX_DRY_RUN_USAGE_DOCS_DEFERRED`

Path A remains valid later for dry-run demo documentation, but it is not the selected next product path.

## Next scope objective

The next scope objective is to define a future controlled write-enabled export contract.

The future contract must specify exactly one minimal controlled output artifact.

The future contract must specify exactly one controlled temporary or fixture-owned output root.

The future contract must specify a strict filename allowlist.

The future contract must specify extension allowlist behavior.

The future contract must specify parent directory boundary checks.

The future contract must specify no overwrite behavior.

The future contract must specify deterministic text content behavior.

The future contract must specify post-write verification requirements.

The future contract must specify cleanup or fixture isolation requirements.

The future contract must specify audit metadata.

The future contract must specify failure behavior.

The future contract must specify rollback expectations if a write attempt fails.

The future contract must specify that real media remains out of scope.

The future contract must specify that scanner execution remains out of scope.

The future contract must specify that ffprobe execution remains out of scope.

The future contract must specify that FFmpeg execution remains out of scope.

The future contract must specify that external process execution remains out of scope.

The future contract must specify that network access remains out of scope.

The future contract must specify that SaaS, database, backend, frontend, installer, client demo, public demo, and production behavior remain out of scope.

## Required future gate sequence

The future sequence must not jump directly to implementation.

The required sequence is:

1. controlled write-enabled export contract.
2. controlled write-enabled export contract QA gate.
3. controlled write-enabled export contract QA gate closure review.
4. controlled write-enabled export implementation readiness gate.
5. controlled write-enabled export implementation readiness QA gate.
6. controlled write-enabled export implementation readiness QA gate closure review.
7. minimal controlled implementation.
8. implementation QA gate.
9. implementation QA gate closure review.
10. controlled execution using fixture-owned output only.
11. controlled execution QA gate.
12. controlled execution QA gate closure review.

## First next allowed phase

The first next allowed phase is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.V1`

That next phase must remain doc/test-only.

That next phase must not implement writing.

That next phase must not create directories.

That next phase must not create artifacts on disk.

## Contract must define write-enabled boundaries

The future contract must define that write-enabled behavior is acceptable only when:

- the output root is controlled.
- the output root is test-owned or fixture-owned.
- the output path remains inside the controlled output root.
- the filename is deterministic.
- the extension is approved.
- parent traversal is rejected.
- absolute unsafe paths are rejected.
- home-relative paths are rejected.
- environment-derived paths are rejected.
- overwrite is rejected by default.
- content is deterministic.
- content hash is computed before write.
- content hash is verified after write.
- the result reports bytes intended.
- the result reports bytes written.
- the result reports content hash before and after.
- the result reports artifact path.
- the result reports write state.
- the result reports cleanup expectations.

## Contract must keep current prohibitions

The future contract must preserve these prohibitions:

- no real media access.
- no scanner execution.
- no ffprobe execution.
- no FFmpeg execution.
- no external process execution.
- no network access.
- no SaaS integration.
- no database changes.
- no backend changes.
- no frontend changes.
- no installer work.
- no client-facing demo.
- no public demo.
- no production use.

## Planning rejection conditions

This planning phase must fail if it:

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
- omits a contract-first sequence.
- omits contract QA gate.
- omits readiness gate.
- omits implementation QA gate.
- omits controlled execution QA gate.
- skips directly to production behavior.

## Explicit non-authorization

This planning phase does not authorize write-enabled export.

This planning phase does not authorize directory creation.

This planning phase does not authorize artifact creation on disk.

This planning phase does not authorize real file writing.

This planning phase does not authorize media scanning.

This planning phase does not authorize real media decoding.

This planning phase does not authorize ffprobe execution.

This planning phase does not authorize FFmpeg execution.

This planning phase does not authorize external process execution.

This planning phase does not authorize audio extraction.

This planning phase does not authorize sync.

This planning phase does not authorize transcription.

This planning phase does not authorize subtitle generation.

This planning phase does not authorize timeline export.

This planning phase does not authorize network access.

This planning phase does not authorize SaaS integration.

This planning phase does not authorize database changes.

This planning phase does not authorize backend changes.

This planning phase does not authorize frontend changes.

This planning phase does not authorize installer work.

This planning phase does not authorize public demo work.

This planning phase does not authorize client-facing demo work.

This planning phase does not authorize production use.

## Planning decision

Path B is selected.

The next product direction is controlled write-enabled export contract-first.

The next phase must be doc/test-only.

The next phase must define boundaries before implementation.

The current project remains dry-run-only.

The current project remains not ready for write-enabled behavior.

The current project remains not ready for directory creation.

The current project remains not ready for artifact creation on disk.

The current project remains not ready for real media execution.

The current project remains not ready for public, client-facing, or production use.

## Next allowed step

The next allowed step is:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.V1`

That next step must remain doc/test-only.
