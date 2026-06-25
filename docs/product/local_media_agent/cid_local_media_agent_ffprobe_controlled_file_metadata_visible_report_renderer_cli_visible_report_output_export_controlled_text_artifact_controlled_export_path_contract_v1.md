# CID Local Media Agent — FFprobe Controlled File Metadata Visible Report Renderer CLI Visible Report Output Export Controlled Text Artifact Controlled Export Path Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.CONTRACT.V1`

## Objective

This contract defines safe path rules for a future controlled text artifact export path.

This phase is documentation and test-only.

It does not add runtime behavior.

It does not modify the controlled export implementation.

It does not write files.

It does not create artifacts on disk.

It does not authorize filesystem export implementation.

It does not authorize any real media workflow.

## Previous Closed Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1`

Previous functional result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_TEXT_ARTIFACT_EXPORT_PATH_CONTRACT`

Previous closure review document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_closure_review_v1.md`

Previous closure review test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_closure_review.py`

Current in-memory implementation script:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py`

## Scope

This contract applies only to a future controlled text artifact export path for already-safe controlled visible report text.

The future path resolver must receive an already-built controlled text artifact descriptor.

The future path resolver must not read media.

The future path resolver must not scan folders.

The future path resolver must not execute ffprobe.

The future path resolver must not execute FFmpeg.

The future path resolver must not spawn subprocesses or processes.

The future path resolver must not access network resources.

The future path resolver must not touch SaaS systems or database systems.

## Controlled Export Path Rules

A future implementation must follow all of these rules:

1. It must accept only a controlled export root selected by an explicit future controlled phase.
2. It must accept only a descriptor produced by the controlled in-memory descriptor builder.
3. It must use only the descriptor `suggested_filename` as the file name candidate.
4. It must reject empty export roots.
5. It must reject empty suggested filenames.
6. It must reject absolute suggested filenames.
7. It must reject parent traversal segments.
8. It must reject path separators in suggested filenames.
9. It must reject Windows drive prefixes.
10. It must reject UNC paths.
11. It must reject hidden dotfile names.
12. It must require the `.controlled_visible_report.txt` suffix.
13. It must resolve the final path under the controlled export root.
14. It must verify the resolved final path remains inside the controlled export root.
15. It must return only a planned path descriptor until a later explicit file-writing phase.
16. It must declare `write_performed` as false.
17. It must declare `artifact_created_on_disk` as false.

## Forbidden Path Inputs

A future implementation must reject path inputs containing any of these patterns:

- `..`
- `/`
- `\`
- drive prefixes such as `C:`
- UNC prefixes
- empty strings
- whitespace-only strings
- hidden dotfile names
- filenames without `.controlled_visible_report.txt`

## Planned Path Descriptor Contract

A future implementation may return a planned path descriptor with these fields:

- `controlled_export_root`
- `suggested_filename`
- `planned_artifact_path`
- `artifact_format`
- `content_sha256`
- `write_performed`
- `artifact_created_on_disk`
- `path_boundary`
- `safety_flags`

The planned path descriptor must not contain real media paths.

The planned path descriptor must not contain arbitrary source folders.

The planned path descriptor must not imply that a file was written.

## Expected Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_CONTRACT_PASS_READY_FOR_QA_GATE`

## Required Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.CONTRACT.QA.GATE.V1`

## Non-Authorization Statement

Closing this contract does not authorize file writing.

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
