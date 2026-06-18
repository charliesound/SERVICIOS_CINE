# CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.V1`

## Objective

This contract defines the safe synthetic fixture data model for the first visible CID Local Media Agent local demo report.

The fixture exists to support a future local demo report generator, but this phase does not create that generator.

This phase is documentation/test-only.

It does not produce report artifacts.

It does not implement a fixture loader.

It does not implement a report generator.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not execute external commands.

It does not scan client folders.

It does not read video files.

It does not read audio files.

It does not modify scanner runtime.

It does not modify SaaS runtime.

It does not create installer behavior.

It does not create licensing or activation behavior.

## Audited baseline

Current stable HEAD before this contract:

`2556383`

Previous QA gate:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.QA.GATE.V1`

Previous gate result:

`PASS_SYNTHETIC_DEMO_REPORT_CONTRACT_READY_FOR_FIXTURE_CONTRACT`

This fixture contract is authorized only as a documentation/test-only step.

## Fixture purpose

The synthetic fixture must provide believable audiovisual project data without exposing or implying any actual client material.

The fixture must allow a future report to show:

- local input label
- safe media-like inventory
- synthetic technical hints
- warning codes
- camera and audio grouping hints
- editorial preparation notes
- postproduction preparation notes
- suggested folder organization
- human review requirements
- demo limitations
- local-only privacy confirmations

The fixture must be useful for a stakeholder-readable demo.

## Fixture identity

The fixture should use this identity:

- `fixture_id`: `SYNTHETIC_LOCAL_DEMO_001`
- `fixture_version`: `v1`
- `fixture_kind`: `synthetic_end_to_end_local_demo_report`
- `privacy_level`: `synthetic_safe_labels_only`
- `local_input_label`: `LOCAL_PROJECT_INPUT_SYNTHETIC`
- `local_output_label`: `LOCAL_PROJECT_OUTPUT_SYNTHETIC_REPORTS`
- `cloud_upload`: `false`
- `external_binary_execution`: `false`
- `client_material_used`: `false`
- `human_review_required`: `true`

## Forbidden fixture content

The fixture must not contain:

- actual project titles
- actual client names
- actual personal names
- actual company names
- private folder paths
- raw camera card names from a client
- raw sound card names from a client
- actual shooting locations
- actual script content
- actual dialogue
- actual audio transcription
- actual filenames from production
- actual technical metadata extracted from files
- GPS data
- email addresses
- phone numbers
- payment data
- license keys
- secrets
- credentials

## Required synthetic item count

The first fixture should contain exactly 10 synthetic inventory items:

- 4 video-like items
- 3 audio-like items
- 1 still-image-like item
- 1 production-document-like item
- 1 ignored or unsupported item

This gives enough variety to demonstrate usefulness without becoming too large.

## Required synthetic inventory items

The fixture must define these safe item identifiers:

- `CAM_A_SYNTHETIC_CLIP_001`
- `CAM_A_SYNTHETIC_CLIP_002`
- `CAM_B_SYNTHETIC_CLIP_001`
- `CAM_B_SYNTHETIC_CLIP_002`
- `AUDIO_SYNTHETIC_TAKE_001`
- `AUDIO_SYNTHETIC_TAKE_002`
- `AUDIO_SYNTHETIC_ROOMTONE_001`
- `STILLS_SYNTHETIC_REFERENCE_001`
- `DOC_SYNTHETIC_NOTES_001`
- `UNSUPPORTED_SYNTHETIC_ITEM_001`

These identifiers are not filenames.

They are safe labels for demo and test purposes.

## Required item fields

Each inventory item must support:

- `safe_item_id`
- `safe_display_label`
- `category`
- `container_hint`
- `codec_hint`
- `duration_hint`
- `frame_rate_hint`
- `resolution_hint`
- `audio_channels_hint`
- `sample_rate_hint`
- `timecode_hint`
- `camera_or_recorder_hint`
- `shooting_day_hint`
- `scene_or_block_hint`
- `sync_candidate_group`
- `language_hint`
- `transcription_readiness`
- `subtitle_readiness`
- `human_review_required`
- `warning_codes`
- `recommended_department_review`

## Required categories

The fixture must use only these categories:

- `video`
- `audio`
- `still_image`
- `production_document`
- `ignored_non_media`

## Required synthetic groups

The fixture must define these sync or review groups:

- `SYNC_GROUP_SYNTHETIC_A`
- `SYNC_GROUP_SYNTHETIC_B`
- `ROOMTONE_GROUP_SYNTHETIC`
- `REFERENCE_GROUP_SYNTHETIC`
- `DOCUMENTATION_GROUP_SYNTHETIC`
- `UNSUPPORTED_GROUP_SYNTHETIC`

These are grouping hints only.

The fixture must not claim that synchronization has been performed.

## Required warning distribution

The fixture must include a controlled warning distribution:

- at least one `MISSING_TIMECODE`
- at least one `POSSIBLE_DOUBLE_SYSTEM_SOUND`
- at least one `FRAME_RATE_MISMATCH`
- at least one `SAMPLE_RATE_MISMATCH`
- at least one `NEEDS_HUMAN_REVIEW`
- at least one `READY_FOR_EDITOR_REVIEW`
- at least one `READY_FOR_DIT_REVIEW`
- at least one `READY_FOR_SOUND_REVIEW`
- at least one `UNSUPPORTED_CONTAINER_HINT`

Warnings are not confirmed errors.

They are synthetic demo indicators.

## Required department review values

The fixture must support these department review labels:

- `EDITORIAL_REVIEW`
- `ASSISTANT_EDITOR_REVIEW`
- `DIT_REVIEW`
- `SOUND_REVIEW`
- `SUBTITLE_REVIEW`
- `PRODUCTION_REVIEW`
- `IGNORE_OR_ARCHIVE_REVIEW`

## Required synthetic project summary

The fixture must include a project-level summary with:

- `total_items`
- `video_like_count`
- `audio_like_count`
- `still_like_count`
- `document_like_count`
- `ignored_or_unsupported_count`
- `sync_candidate_group_count`
- `items_requiring_human_review_count`
- `privacy_mode`
- `demo_mode`
- `limitations_label`

## Required report-ready narrative notes

The fixture must include safe narrative notes for the future report:

- executive summary note
- local-only privacy note
- editorial preparation note
- postproduction risk note
- suggested organization note
- subtitle readiness note
- DaVinci future export readiness note
- limitations note
- next recommended actions note

These notes must be generic and synthetic.

They must not include story, script, client, location, or production-specific details.

## Required suggested folder organization

The fixture must include these suggested folders:

- `01_VIDEO`
- `02_AUDIO`
- `03_STILLS`
- `04_DOCUMENTS`
- `05_REPORTS`
- `06_REVIEW_NEEDED`
- `07_EXPORTS_FOR_EDIT`

The future report may display this organization.

The fixture must not authorize moving, renaming, deleting, copying, or modifying files.

## Required privacy assertions

The fixture must include assertions equivalent to:

- no video upload
- no audio upload
- no client material used
- no cloud processing
- no external binary execution
- no private path exposure
- safe labels only
- human review required

## Required future fixture file shape

A future implementation may store the fixture as JSON.

Recommended future location:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

This phase does not create that JSON file.

The exact file location must be confirmed in the future fixture implementation phase.

## Fixture validation rules

A future fixture validator should reject the fixture if:

- item count is not exactly 10
- required safe item identifiers are missing
- categories are outside the allowed set
- required warning distribution is missing
- a private path appears
- a raw client-like filename appears
- dialogue content appears
- transcription content appears
- actual project names appear
- local-only assertions are missing
- human review is not required
- the fixture claims completed sync
- the fixture claims completed transcription
- the fixture claims completed translation
- the fixture claims completed DaVinci export

## Acceptance criteria for this contract

This contract is accepted only if:

- the phase remains documentation/test-only
- only this document and its unit test are changed
- no fixture JSON is created
- no reporting generator component is created
- no runtime file is modified
- no scanner runtime file is modified
- no SaaS runtime file is modified
- no external command execution is introduced
- no client material is included
- the fixture identity is defined
- the required item list is complete
- the required item fields are complete
- the warning distribution is defined
- the department review labels are defined
- the privacy assertions are explicit
- the validation rules are explicit
- the next phase remains gated

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1`

After that, the likely path should be:

1. fixture contract QA gate
2. synthetic fixture schema contract
3. synthetic fixture JSON implementation readiness gate
4. synthetic fixture JSON minimal implementation
5. synthetic fixture QA
6. synthetic demo report generator readiness gate

## Final contract decision

Contract decision:

`SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_QA`

This phase authorizes QA of the fixture contract only.

It does not authorize fixture implementation.

It does not authorize report generation.
