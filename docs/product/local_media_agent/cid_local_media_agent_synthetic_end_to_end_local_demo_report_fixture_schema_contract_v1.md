# CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture Schema Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1`

## Objective

This contract defines the exact JSON schema expected for the future synthetic demo report fixture.

The schema belongs to the CID Local Media Agent standalone product line.

This phase keeps the work documentation/test-only.

It defines the structure, required fields, allowed values, cardinality, privacy rules, and validation expectations for the future fixture.

This phase leaves actual fixture data creation for a later gated phase.

This phase leaves loader code for a later gated phase.

This phase leaves report generation code for a later gated phase.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not execute external commands.

It does not scan folders.

It does not read video files.

It does not read audio files.

It does not modify scanner runtime.

It does not modify SaaS runtime.

It does not create installer behavior.

It does not create licensing or activation behavior.

## Audited baseline

Current stable HEAD before this schema contract:

`4f0a378`

Previous QA gate:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1`

Previous QA gate result:

`PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_SCHEMA_CONTRACT`

Standalone product blueprint:

`CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1`

## Schema identity

The future JSON fixture must identify itself with:

- `schema_version`: `cid_local_media_agent_synthetic_demo_report_fixture_schema_v1`
- `fixture_id`: `SYNTHETIC_LOCAL_DEMO_001`
- `fixture_version`: `v1`
- `fixture_kind`: `synthetic_end_to_end_local_demo_report`
- `privacy_level`: `synthetic_safe_labels_only`
- `source_mode`: `synthetic_contract`
- `created_for_product`: `CID Local Media Agent`
- `created_for_ecosystem`: `CID — Cinematic Intelligence Direction`
- `created_for_phase`: `CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1`

## Root object schema

The future JSON root must be an object.

Required root fields:

- `schema_version`
- `fixture_id`
- `fixture_version`
- `fixture_kind`
- `privacy_level`
- `source_mode`
- `created_for_product`
- `created_for_ecosystem`
- `local_input_label`
- `local_output_label`
- `cloud_upload`
- `external_binary_execution`
- `client_material_used`
- `human_review_required`
- `limitations`
- `items`
- `project_summary`
- `suggested_folders`
- `privacy_assertions`
- `validation_rules`
- `next_recommended_phase`

No extra root field should be allowed unless a future schema version explicitly adds it.

## Root field types

Expected root field types:

- `schema_version`: string
- `fixture_id`: string
- `fixture_version`: string
- `fixture_kind`: string
- `privacy_level`: string
- `source_mode`: string
- `created_for_product`: string
- `created_for_ecosystem`: string
- `local_input_label`: string
- `local_output_label`: string
- `cloud_upload`: boolean
- `external_binary_execution`: boolean
- `client_material_used`: boolean
- `human_review_required`: boolean
- `limitations`: array of strings
- `items`: array of objects
- `project_summary`: object
- `suggested_folders`: array of strings
- `privacy_assertions`: object
- `validation_rules`: object
- `next_recommended_phase`: string

## Required root values

The following root values must be exact:

- `schema_version`: `cid_local_media_agent_synthetic_demo_report_fixture_schema_v1`
- `fixture_id`: `SYNTHETIC_LOCAL_DEMO_001`
- `fixture_version`: `v1`
- `fixture_kind`: `synthetic_end_to_end_local_demo_report`
- `privacy_level`: `synthetic_safe_labels_only`
- `source_mode`: `synthetic_contract`
- `created_for_product`: `CID Local Media Agent`
- `created_for_ecosystem`: `CID — Cinematic Intelligence Direction`
- `local_input_label`: `LOCAL_PROJECT_INPUT_SYNTHETIC`
- `local_output_label`: `LOCAL_PROJECT_OUTPUT_SYNTHETIC_REPORTS`
- `cloud_upload`: `false`
- `external_binary_execution`: `false`
- `client_material_used`: `false`
- `human_review_required`: `true`
- `next_recommended_phase`: `CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.V1`

## Items array rules

The `items` array must contain exactly 10 objects.

The future JSON fixture must include exactly these safe item identifiers:

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

No duplicate `safe_item_id` is allowed.

No item may use a raw filename.

No item may use a private folder path.

No item may use a client name, person name, real place, production title, scene title, script excerpt, dialogue excerpt, or transcription excerpt.

## Item object required fields

Each item object must include:

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
- `report_notes`

No extra item field should be allowed unless a future schema version explicitly adds it.

## Item field types

Expected item field types:

- `safe_item_id`: string
- `safe_display_label`: string
- `category`: string
- `container_hint`: string or null
- `codec_hint`: string or null
- `duration_hint`: string or null
- `frame_rate_hint`: string or null
- `resolution_hint`: string or null
- `audio_channels_hint`: string or null
- `sample_rate_hint`: string or null
- `timecode_hint`: string or null
- `camera_or_recorder_hint`: string or null
- `shooting_day_hint`: string
- `scene_or_block_hint`: string
- `sync_candidate_group`: string
- `language_hint`: string
- `transcription_readiness`: string
- `subtitle_readiness`: string
- `human_review_required`: boolean
- `warning_codes`: array of strings
- `recommended_department_review`: array of strings
- `report_notes`: array of strings

## Allowed categories

Allowed `category` values:

- `video`
- `audio`
- `still_image`
- `production_document`
- `ignored_non_media`

Required category distribution:

- `video`: 4 items
- `audio`: 3 items
- `still_image`: 1 item
- `production_document`: 1 item
- `ignored_non_media`: 1 item

## Allowed synthetic groups

Allowed `sync_candidate_group` values:

- `SYNC_GROUP_SYNTHETIC_A`
- `SYNC_GROUP_SYNTHETIC_B`
- `ROOMTONE_GROUP_SYNTHETIC`
- `REFERENCE_GROUP_SYNTHETIC`
- `DOCUMENTATION_GROUP_SYNTHETIC`
- `UNSUPPORTED_GROUP_SYNTHETIC`

Expected group distribution:

- `SYNC_GROUP_SYNTHETIC_A`: at least 2 items
- `SYNC_GROUP_SYNTHETIC_B`: at least 2 items
- `ROOMTONE_GROUP_SYNTHETIC`: at least 1 item
- `REFERENCE_GROUP_SYNTHETIC`: at least 1 item
- `DOCUMENTATION_GROUP_SYNTHETIC`: at least 1 item
- `UNSUPPORTED_GROUP_SYNTHETIC`: at least 1 item

## Allowed warning codes

Allowed `warning_codes` values:

- `MISSING_TIMECODE`
- `POSSIBLE_DOUBLE_SYSTEM_SOUND`
- `FRAME_RATE_MISMATCH`
- `SAMPLE_RATE_MISMATCH`
- `NEEDS_HUMAN_REVIEW`
- `READY_FOR_EDITOR_REVIEW`
- `READY_FOR_DIT_REVIEW`
- `READY_FOR_SOUND_REVIEW`
- `READY_FOR_SUBTITLE_REVIEW`
- `UNSUPPORTED_CONTAINER_HINT`
- `NO_WARNINGS`

Required warning coverage:

- at least one item must include `MISSING_TIMECODE`
- at least one item must include `POSSIBLE_DOUBLE_SYSTEM_SOUND`
- at least one item must include `FRAME_RATE_MISMATCH`
- at least one item must include `SAMPLE_RATE_MISMATCH`
- at least one item must include `NEEDS_HUMAN_REVIEW`
- at least one item must include `READY_FOR_EDITOR_REVIEW`
- at least one item must include `READY_FOR_DIT_REVIEW`
- at least one item must include `READY_FOR_SOUND_REVIEW`
- at least one item must include `UNSUPPORTED_CONTAINER_HINT`

## Allowed department review values

Allowed `recommended_department_review` values:

- `EDITORIAL_REVIEW`
- `ASSISTANT_EDITOR_REVIEW`
- `DIT_REVIEW`
- `SOUND_REVIEW`
- `SUBTITLE_REVIEW`
- `PRODUCTION_REVIEW`
- `IGNORE_OR_ARCHIVE_REVIEW`

Required department coverage:

- at least one item must include `EDITORIAL_REVIEW`
- at least one item must include `ASSISTANT_EDITOR_REVIEW`
- at least one item must include `DIT_REVIEW`
- at least one item must include `SOUND_REVIEW`
- at least one item must include `SUBTITLE_REVIEW`
- at least one item must include `PRODUCTION_REVIEW`
- at least one item must include `IGNORE_OR_ARCHIVE_REVIEW`

## Project summary object

The `project_summary` object must include:

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

Expected `project_summary` values:

- `total_items`: 10
- `video_like_count`: 4
- `audio_like_count`: 3
- `still_like_count`: 1
- `document_like_count`: 1
- `ignored_or_unsupported_count`: 1
- `sync_candidate_group_count`: 6
- `privacy_mode`: `synthetic_safe_labels_only`
- `demo_mode`: `synthetic_end_to_end_local_demo`
- `limitations_label`: `synthetic_demo_not_real_media_analysis`

`items_requiring_human_review_count` must be an integer greater than or equal to 1.

## Suggested folders

The `suggested_folders` array must include exactly:

- `01_VIDEO`
- `02_AUDIO`
- `03_STILLS`
- `04_DOCUMENTS`
- `05_REPORTS`
- `06_REVIEW_NEEDED`
- `07_EXPORTS_FOR_EDIT`

## Privacy assertions object

The `privacy_assertions` object must include these boolean fields:

- `uses_synthetic_labels_only`
- `contains_real_client_media`
- `contains_private_paths`
- `contains_raw_filenames`
- `contains_client_names`
- `contains_person_names`
- `contains_real_locations`
- `contains_script_content`
- `contains_dialogue_content`
- `contains_transcription_content`
- `requires_cloud_upload`
- `requires_external_binary_execution`
- `safe_for_public_demo_after_human_review`

Expected privacy assertion values:

- `uses_synthetic_labels_only`: `true`
- `contains_real_client_media`: `false`
- `contains_private_paths`: `false`
- `contains_raw_filenames`: `false`
- `contains_client_names`: `false`
- `contains_person_names`: `false`
- `contains_real_locations`: `false`
- `contains_script_content`: `false`
- `contains_dialogue_content`: `false`
- `contains_transcription_content`: `false`
- `requires_cloud_upload`: `false`
- `requires_external_binary_execution`: `false`
- `safe_for_public_demo_after_human_review`: `false`

The last value stays false because a later human review must approve any public-facing use.

## Validation rules object

The `validation_rules` object must include:

- `exact_item_count_required`
- `unique_safe_item_ids_required`
- `allowed_categories_only`
- `allowed_warning_codes_only`
- `allowed_department_reviews_only`
- `private_paths_rejected`
- `raw_filenames_rejected`
- `real_names_rejected`
- `script_content_rejected`
- `dialogue_content_rejected`
- `transcription_content_rejected`
- `cloud_upload_rejected`
- `external_binary_execution_rejected`
- `human_review_required`

Expected validation rule values:

- `exact_item_count_required`: `true`
- `unique_safe_item_ids_required`: `true`
- `allowed_categories_only`: `true`
- `allowed_warning_codes_only`: `true`
- `allowed_department_reviews_only`: `true`
- `private_paths_rejected`: `true`
- `raw_filenames_rejected`: `true`
- `real_names_rejected`: `true`
- `script_content_rejected`: `true`
- `dialogue_content_rejected`: `true`
- `transcription_content_rejected`: `true`
- `cloud_upload_rejected`: `true`
- `external_binary_execution_rejected`: `true`
- `human_review_required`: `true`

## Limitations array

The `limitations` array must include human-readable limitations.

Required limitation meanings:

- synthetic demo data
- no real media analysis
- no completed synchronization
- no completed transcription
- no completed subtitle translation
- no completed DaVinci export
- human review required
- local-first privacy promise
- future implementation required

## Future fixture file path

The future JSON fixture may be created later at:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

This schema contract does not create that file.

## Rejection rules

A future fixture must be rejected if:

- root required fields are missing
- item required fields are missing
- item count is not exactly 10
- safe item identifiers are duplicated
- unknown categories appear
- unknown warning codes appear
- unknown department review values appear
- private paths appear
- raw filenames appear
- names that look like client, person, or production names appear
- real locations appear
- story or script content appears
- dialogue content appears
- transcription content appears
- media upload is required
- external binary execution is required
- human review is disabled
- public demo safety is marked true before human review

## Non-goals for this schema contract

This schema contract does not authorize:

- fixture JSON creation
- fixture loader creation
- report generation
- runtime code
- scanner changes
- ffprobe execution
- ffmpeg execution
- transcription
- subtitle translation
- DaVinci export
- SaaS integration
- installer creation
- license server integration
- payment integration
- client media processing

## Acceptance criteria

This schema contract is accepted only if:

- root schema is defined
- item schema is defined
- exact item count is defined
- safe item identifiers are fixed
- allowed categories are constrained
- category distribution is defined
- allowed synthetic groups are constrained
- warning codes are constrained
- warning coverage is defined
- department review values are constrained
- project summary shape is defined
- suggested folders are defined
- privacy assertions are defined
- validation rules are defined
- rejection rules are defined
- non-goals are explicit
- next phase remains gated

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.QA.GATE.V1`

The next phase should audit this schema contract before any future JSON fixture is created.

## Final decision

Schema contract decision:

`SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_QA`

This decision authorizes only the next documentation/test-only QA gate.

It does not authorize fixture JSON creation.

It does not authorize a loader.

It does not authorize report generation.

It does not authorize runtime changes.
