# CID Local Media Agent — FFprobe Controlled File Metadata Visible Report Renderer CLI Visible Report Output Export Controlled Text Artifact Controlled Export Path Planner Implementation Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.CONTRACT.V1`

## Objective

This contract defines the allowed boundary for a future controlled export path planner implementation.

This phase is documentation and test-only.

It does not add runtime behavior.

It does not implement a path planner.

It does not implement a path resolver.

It does not modify the controlled export implementation.

It does not write files.

It does not create directories.

It does not create artifacts on disk.

It does not authorize filesystem export implementation.

It does not authorize any real media workflow.

## Previous Closed Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1`

Previous functional result:

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_CONTRACT`

Previous readiness QA gate closure review document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review_v1.md`

Previous readiness QA gate closure review test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review.py`

Readiness QA gate document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_v1.md`

Readiness QA gate test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate.py`

Readiness contract document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_v1.md`

Readiness contract test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract.py`

Path contract document:

`docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract_v1.md`

Path contract test:

`tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract.py`

Current in-memory descriptor builder:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py`

## Future Implementation Boundary

A later controlled implementation phase may add only a pure path planner.

That future planner must be deterministic.

That future planner must be local-only.

That future planner must be side-effect free.

That future planner must only calculate and return a planned path descriptor.

That future planner must not write files.

That future planner must not create directories.

That future planner must not create artifacts on disk.

That future planner must not scan folders.

That future planner must not execute ffprobe or FFmpeg.

That future planner must not execute subprocesses or external processes.

That future planner must not access the network.

That future planner must not touch SaaS, database, installer, or client-facing code.

## Future Module Boundary

A later controlled implementation phase may add a dedicated local media agent planner module only under:

`scripts/local_media_agent/`

The future module must be importable by tests without side effects.

The future module must not perform work at import time.

The future module must not parse command-line arguments.

The future module must not read environment variables.

The future module must not read configuration files.

The future module must not access real media.

The future module must not access arbitrary folders.

The future module must not open, read, write, or delete files.

## Future Planner Function Boundary

A later controlled implementation phase may define one pure planner function.

The function may accept only:

1. `controlled_export_root`
2. A controlled descriptor produced by the existing in-memory descriptor builder.

The function may return only a planned path descriptor.

The function must not return opened file handles.

The function must not return executable commands.

The function must not return shell strings.

The function must not return write instructions.

The function must not return a claim that an artifact exists on disk.

## Required Future Input Validation

The future planner must reject:

1. Missing controlled export root.
2. Empty controlled export root.
3. Whitespace-only controlled export root.
4. Missing descriptor.
5. Descriptor without `suggested_filename`.
6. Empty suggested filename.
7. Whitespace-only suggested filename.
8. Absolute suggested filename.
9. Parent traversal segments.
10. Path separators in the suggested filename.
11. Windows drive prefixes.
12. UNC path forms.
13. Hidden dotfile names.
14. Suggested filename without the `.controlled_visible_report.txt` suffix.
15. Any final resolved path outside the controlled export root.

## Required Future Planned Path Descriptor

The future planned path descriptor must include:

1. `controlled_export_root`
2. `suggested_filename`
3. `planned_artifact_path`
4. `artifact_format`
5. `content_sha256`
6. `write_performed`
7. `artifact_created_on_disk`
8. `path_boundary`
9. `safety_flags`

The future planned path descriptor must declare:

1. `write_performed` as false.
2. `artifact_created_on_disk` as false.
3. `path_boundary` as controlled.
4. `artifact_format` as controlled visible report text.
5. Safety flags confirming no real media access.
6. Safety flags confirming no scanner execution.
7. Safety flags confirming no ffprobe execution.
8. Safety flags confirming no FFmpeg execution.
9. Safety flags confirming no subprocess execution.
10. Safety flags confirming no network access.
11. Safety flags confirming no SaaS or database integration.
12. Safety flags confirming no file write.

## Required Future Test Boundary

A later controlled implementation phase must add tests proving:

1. Valid controlled root plus valid descriptor returns a planned descriptor.
2. The planned descriptor remains inside the controlled export root.
3. Empty roots are rejected.
4. Empty suggested filenames are rejected.
5. Absolute suggested filenames are rejected.
6. Parent traversal is rejected.
7. Path separators are rejected.
8. Windows drive prefixes are rejected.
9. UNC path forms are rejected.
10. Hidden dotfile names are rejected.
11. Wrong suffixes are rejected.
12. `write_performed` remains false.
13. `artifact_created_on_disk` remains false.
14. No file is created on disk by the planner tests.
15. No directory is created on disk by the planner tests.
16. The current in-memory descriptor builder remains compatible.

## Explicit Contract Boundary

This contract is not an implementation.

This contract is not a QA gate.

This contract is not a file-writing contract.

This contract is not an artifact-generation contract.

This contract only defines what a future controlled implementation phase may implement.

## Expected Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE`

## Required Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.CONTRACT.QA.GATE.V1`

## Non-Authorization Statement

Closing this contract does not authorize path planner implementation.

It does not authorize path resolver implementation.

It does not authorize file writing.

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
