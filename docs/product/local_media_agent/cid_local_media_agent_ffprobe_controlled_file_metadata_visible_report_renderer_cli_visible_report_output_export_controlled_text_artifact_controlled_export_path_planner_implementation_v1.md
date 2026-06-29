# CID Local Media Agent — FFprobe Controlled File Metadata Visible Report Renderer CLI Visible Report Output Export Controlled Text Artifact Controlled Export Path Planner Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.V1`

## Previous Closed Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.READINESS.GATE.QA.GATE.CLOSURE.REVIEW.V1`

Previous functional result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_PATH_PLANNER_IMPLEMENTATION_PHASE`

## Objective

Implement the first controlled pure export path planner.

This implementation is intentionally narrow.

It calculates a planned path descriptor only.

It does not write files.

It does not create directories.

It does not create artifacts on disk.

It does not scan folders.

It does not execute ffprobe or FFmpeg.

It does not execute subprocesses or external processes.

It does not access the network.

It does not touch SaaS, database, backend, frontend, installer, or client-facing code.

## Implemented Module

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner.py`

## Implemented Function

`plan_controlled_text_artifact_export_path`

## Allowed Inputs

The function accepts only:

1. `controlled_export_root`
2. `controlled_descriptor`

The descriptor must include `suggested_filename`.

## Implemented Rejections

The planner rejects:

1. Missing controlled export root.
2. Empty controlled export root.
3. Whitespace-only controlled export root.
4. Missing descriptor.
5. Descriptor without `suggested_filename`.
6. Empty suggested filename.
7. Whitespace-only suggested filename.
8. Parent traversal segments.
9. Path separators in the suggested filename.
10. Windows drive prefixes.
11. UNC path forms.
12. Hidden dotfile names.
13. Suggested filename without the `.controlled_visible_report.txt` suffix.
14. Any planned path outside the controlled export root.

## Returned Descriptor

The planner returns:

1. `controlled_export_root`
2. `suggested_filename`
3. `planned_artifact_path`
4. `artifact_format`
5. `content_sha256`
6. `write_performed`
7. `artifact_created_on_disk`
8. `path_boundary`
9. `safety_flags`

`write_performed` is always false.

`artifact_created_on_disk` is always false.

## Expected Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_PASS_READY_FOR_QA_GATE`

## Required Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.QA.GATE.V1`

## Non-Authorization Statement

This implementation does not authorize file writing.

It does not authorize directory creation.

It does not authorize artifact generation on disk.

It does not authorize real media.

It does not authorize arbitrary folders.

It does not authorize scanner execution.

It does not authorize ffprobe or FFmpeg execution.

It does not authorize subprocess or process execution.

It does not authorize audio extraction.

It does not authorize sync.

It does not authorize transcription.

It does not authorize subtitles.

It does not authorize timeline export.

It does not authorize network access.

It does not authorize SaaS or database integration.

It does not authorize installer work.

It does not authorize public demo, client demo, sales demo, or production use.
