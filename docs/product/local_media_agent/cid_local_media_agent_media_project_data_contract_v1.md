# CID Local Media Agent — Media Project Data Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.MEDIA_PROJECT.DATA_CONTRACT.V1`

## Objective

This document defines the local data contract for **CID Local Media Agent**, the local execution layer used by **CID Editing Intelligence**.

The contract represents local media projects, scanned assets, technical metadata, sync candidates, sync results, multilingual transcripts, Spanish translated working subtitles, editorial selects, and DaVinci Resolve rough-cut assist exports.

This phase is documentation/test-only.

It does not implement a scanner, FFmpeg adapter, ffprobe adapter, sync engine, waveform analysis, transcription, translation, DaVinci export, licensing, installer, iLok/PACE integration, SaaS integration, database model, migration, API route, frontend, worker, Docker configuration, or real media processing.

## SaaS isolation rule

This contract is local-only and must remain isolated from CID SaaS.

It must not touch CID SaaS runtime, backend routes, database models, Alembic migrations, Docker configuration, frontend code, Stripe/payment code, AI Jobs runtime, credits, ledger, workers, production configuration, or integration code.

Future SaaS integration requires a separate explicit phase.

## Privacy rule

Original media never leaves the client system.

The contract must not require uploading camera originals, sound originals, video files, audio files, proxies, extracted WAV files, temporary analysis files, frames, thumbnails, transcripts, subtitles, or editorial summaries.

Transcripts, subtitles, and summaries may only leave the local system with explicit client authorization in a future connected mode.

## ProjectManifest

A local project must be represented by `ProjectManifest`.

Required conceptual fields:

- `schema_version`
- `project_id`
- `project_name_local`
- `created_at`
- `updated_at`
- `input_roots`
- `output_root`
- `privacy_mode`
- `local_only`
- `media_never_uploaded`
- `assets`
- `sync_candidates`
- `sync_results`
- `transcripts`
- `subtitle_tracks`
- `editorial_selects`
- `davinci_exports`
- `warnings`
- `human_review_required`

## Path policy

Every file reference must declare a path policy.

Allowed path policies:

- `local_absolute_path`
- `local_relative_path`
- `sanitized_path`
- `hashed_path`
- `redacted_path`
- `client_controlled_local_output`

Local CLI execution may use absolute paths internally.

Connected reports must prefer sanitized, hashed, or redacted paths.

Full local paths must not be sent to CID SaaS without explicit permission.

## MediaAsset

All discovered or generated local files must be represented as `MediaAsset`.

Required conceptual fields:

- `asset_id`
- `media_type`
- `source_kind`
- `path`
- `path_policy`
- `file_name`
- `extension`
- `file_size_bytes`
- `technical_metadata`
- `privacy`
- `warnings`
- `human_review_required`

Allowed `media_type` values: `video`, `audio`, `sidecar`, `unknown`.

Allowed `source_kind` values: `camera_original`, `production_sound`, `proxy`, `sidecar_metadata`, `generated_local_output`, `temporary_analysis_file`.

## TechnicalMetadata

Technical metadata may be populated by ffprobe or another local inspection layer.

Required conceptual fields:

- `container`
- `codec_video`
- `codec_audio`
- `duration_seconds`
- `frame_rate`
- `timecode_start`
- `timecode_end`
- `sample_rate`
- `audio_channels`
- `resolution`
- `bit_depth`
- `stream_count`
- `has_video`
- `has_audio`
- `has_scratch_audio`
- `metadata_source`
- `metadata_warnings`

Allowed `metadata_source` values: `ffprobe`, `sidecar`, `manual_entry`, `derived`, `unknown`.

## VideoClip

A `VideoClip` extends `MediaAsset`.

Additional conceptual fields:

- `camera_id`
- `camera_roll`
- `clip_name`
- `scene`
- `take`
- `fps`
- `timecode_start`
- `timecode_end`
- `has_scratch_audio`
- `scratch_audio_quality`
- `linked_audio_asset_ids`
- `sync_status`

Allowed `sync_status` values: `not_processed`, `matched_by_timecode`, `matched_by_name`, `matched_by_waveform`, `matched_by_slate`, `manual_review_required`, `failed`.

## AudioClip

An `AudioClip` extends `MediaAsset`.

Additional conceptual fields:

- `recorder_id`
- `sound_roll`
- `track_names`
- `channel_layout`
- `sample_rate`
- `bit_depth`
- `timecode_start`
- `timecode_end`
- `scene`
- `take`
- `linked_video_asset_ids`
- `sync_status`

## SyncCandidate

A `SyncCandidate` represents a possible video/audio match.

Required conceptual fields:

- `candidate_id`
- `video_asset_id`
- `audio_asset_id`
- `candidate_methods`
- `timecode_match`
- `name_match`
- `duration_match`
- `waveform_match`
- `slate_match`
- `estimated_offset_seconds`
- `confidence`
- `warnings`
- `human_review_required`

Allowed candidate methods: `timecode`, `scene_take_roll_name`, `duration_similarity`, `waveform`, `slate`, `manual`.

Allowed confidence values: `high`, `medium`, `low`, `failed`, `manual_review_required`.

## SyncResult

A `SyncResult` represents the selected sync decision.

Required conceptual fields:

- `sync_result_id`
- `video_asset_id`
- `audio_asset_id`
- `selected_method`
- `offset_seconds`
- `confidence`
- `drift_detected`
- `drift_notes`
- `is_final`
- `human_review_required`
- `review_status`
- `warnings`

Allowed selected methods: `timecode`, `scene_take_roll_name`, `waveform`, `slate`, `manual`, `failed`.

Allowed review statuses: `not_required`, `pending`, `approved`, `rejected`, `needs_adjustment`.

An uncertain sync must not be marked as final.

## TranscriptSegment

A `TranscriptSegment` stores original-language speech recognition output.

Required conceptual fields:

- `segment_id`
- `asset_id`
- `sync_result_id`
- `start_time_seconds`
- `end_time_seconds`
- `speaker_id`
- `detected_language`
- `language_confidence`
- `original_text`
- `transcription_confidence`
- `requires_human_review`
- `warnings`

The original transcript must be preserved separately from translations.

## SubtitleTrack

A `SubtitleTrack` represents original or translated subtitles.

Required conceptual fields:

- `subtitle_track_id`
- `asset_id`
- `sync_result_id`
- `track_kind`
- `source_language`
- `target_language`
- `format`
- `segments`
- `is_working_subtitle`
- `is_final_subtitle`
- `human_validation_required`
- `warnings`

Allowed `track_kind` values: `original_language`, `spanish_translation`, `bilingual_original_plus_spanish`, `review_notes`.

Allowed subtitle formats: `srt`, `vtt`, `json_segments`, `davinci_importable_srt`.

Spanish translated subtitles must use target language `es`.

Automatically generated Spanish subtitles are working subtitles unless human validated.

## SpanishSubtitleSegment

A Spanish translated subtitle segment must include `subtitle_segment_id`, `source_segment_id`, `start_time_seconds`, `end_time_seconds`, `source_language`, `target_language`, `original_text_reference`, `spanish_text`, `translation_confidence`, `is_working_translation`, `human_validation_required`, and `warnings`.

The contract must preserve the original text reference for human review.

## EditorialSelect

An `EditorialSelect` represents a moment useful for editing.

Required conceptual fields:

- `select_id`
- `asset_id`
- `sync_result_id`
- `start_time_seconds`
- `end_time_seconds`
- `reason`
- `editorial_value`
- `summary_es`
- `detected_language`
- `spanish_subtitle_available`
- `suggested_use`
- `human_review_required`

Allowed editorial values: `high`, `medium`, `low`, `discard`, `unknown`.

Allowed suggested uses: `rough_cut`, `teaser`, `character_moment`, `story_context`, `technical_review`, `subtitle_review`, `translator_review`, `manual_review`.

## DavinciExportPackage

A `DavinciExportPackage` represents local outputs prepared for DaVinci Resolve.

Required conceptual fields:

- `export_id`
- `export_kind`
- `output_directory`
- `path_policy`
- `timeline_name`
- `select_ids`
- `subtitle_track_ids`
- `marker_file`
- `subtitle_file_es`
- `otio_file`
- `edl_file`
- `fcpxml_file`
- `import_instructions`
- `is_final_edit`
- `is_rough_cut_assist`
- `warnings`
- `human_review_required`

Allowed export kinds: `selects_timeline`, `rough_cut_assist`, `subtitle_package`, `marker_package`, `review_package`.

The export must be positioned as a rough-cut assist, not a final automatic edit.

## Human review flags

The contract must support human review at every major stage:

- scan review
- sync review
- transcript review
- translation review
- subtitle review
- editorial select review
- DaVinci export review

Human review fields must never be removed to make the product appear more automatic than it is.

## Local output layout

A compliant local project output may use this layout:

- `CID_OUTPUT/00_project/project_manifest.json`
- `CID_OUTPUT/01_media_catalog/media_catalog.json`
- `CID_OUTPUT/02_sync/sync_candidates.json`
- `CID_OUTPUT/02_sync/sync_results.json`
- `CID_OUTPUT/03_transcripts_original/transcripts_original.json`
- `CID_OUTPUT/04_subtitles_spanish/subtitles_es_working.json`
- `CID_OUTPUT/05_editorial_summary/editorial_selects.json`
- `CID_OUTPUT/06_davinci/rough_cut_selects.otio`
- `CID_OUTPUT/06_davinci/rough_cut_markers.csv`
- `CID_OUTPUT/06_davinci/timeline_subtitles_es.srt`
- `CID_OUTPUT/06_davinci/import_instructions.md`

## Non-goals of this phase

This phase does not implement dataclasses, Pydantic models, JSON schema files, a scanner, ffprobe calls, ffmpeg calls, real media processing, private disk access, SRT generation, transcription, translation, DaVinci timelines, CLI commands, licensing, iLok/PACE, SaaS runtime, backend routes, database models, Alembic, Docker, frontend, Stripe, AI Jobs, credits, ledger, or production configuration.

## Acceptance criteria

This phase is accepted when:

- the local-only project contract is documented
- key entities are named consistently
- local-only media privacy is preserved
- Spanish translated subtitles are represented separately from original transcripts
- DaVinci rough-cut assist outputs are represented
- human review is represented at scan, sync, transcript, subtitle, editorial, and export stages
- explicit non-goals protect CID SaaS from accidental integration work
