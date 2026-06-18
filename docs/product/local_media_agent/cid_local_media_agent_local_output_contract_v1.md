# CID Local Media Agent — Local Output Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.LOCAL_OUTPUT.CONTRACT.V1`

## Objective

This document defines the local output folder and file contract for **CID Local Media Agent**, the local execution layer used by **CID Editing Intelligence**.

The output contract defines where the app/CLI writes project manifests, media catalogs, ffprobe summaries, sync candidates, sync results, multilingual original transcripts, Spanish translated working subtitles, editorial summaries, DaVinci Resolve rough-cut assist exports, temporary analysis files, logs, warnings, and human review files.

This phase is documentation/test-only.

It does not implement a scanner, FFmpeg adapter, ffprobe adapter, sync engine, waveform analysis, transcription, translation, DaVinci export, licensing, installer, iLok/PACE integration, SaaS integration, database model, migration, API route, frontend, worker, Docker configuration, or real media processing.

## SaaS isolation rule

This contract is local-only and must remain isolated from CID SaaS.

It must not touch CID SaaS runtime, backend routes, database models, Alembic migrations, Docker configuration, frontend code, Stripe/payment code, AI Jobs runtime, credits, ledger, workers, production configuration, or integration code.

Future SaaS integration requires a separate explicit phase.

## Privacy rule

Original media never leaves the client system.

The output folder must not contain copied camera originals, copied sound originals, copied video files, copied audio files, or copied proxies.

The output folder must not contain copied camera originals.
The output folder must not contain copied sound originals.

The output folder may contain local generated artifacts such as catalogs, reports, temporary audio analysis files, transcription artifacts, subtitles, editorial summaries, sync maps, DaVinci package files, and logs.

Temporary files must remain local and must be stored under the configured output root.

Transcripts, subtitles, summaries, paths, logs, or metadata may only leave the local system with explicit client authorization in a future connected mode.

## Output root

The app must write all generated files under a client-controlled local output root.

Default conceptual root:

`CID_OUTPUT/`

The app must not write generated files beside original media unless the client explicitly chooses that location.

The app must not rename, move, delete, rewrite, or modify original media.

## Required top-level layout

A compliant output root must use these top-level folders:

- `00_project/`
- `01_media_catalog/`
- `02_sync/`
- `03_transcripts_original/`
- `04_subtitles_spanish/`
- `05_editorial_summary/`
- `06_davinci/`
- `90_temp/`
- `99_logs/`

The numeric prefix is intentional and must keep the workflow readable for editors, assistants, producers, and technical users.

## 00_project

The `00_project/` folder stores project-level local control files.

Required files:

- `project_manifest.json`
- `processing_status.json`
- `privacy_report.md`
- `human_review_index.md`
- `output_contract_version.txt`

Purpose:

- identify the local project;
- declare schema and output contract version;
- record local-only privacy mode;
- summarize processing state;
- list human review requirements;
- make clear that original media was not uploaded.

## 01_media_catalog

The `01_media_catalog/` folder stores local media scan outputs.

Required files:

- `media_catalog.json`
- `media_catalog.csv`
- `media_catalog.md`
- `ffprobe_summary.json`
- `scan_warnings.json`
- `manual_media_review.csv`

Purpose:

- list discovered media assets;
- summarize technical metadata;
- expose ffprobe-derived metadata;
- mark missing or ambiguous metadata;
- identify clips requiring human review.

This folder must not contain copied camera originals, copied sound originals, copied proxies, or extracted full-quality media.

## 02_sync

The `02_sync/` folder stores synchronization outputs.

Required files:

- `sync_candidates.json`
- `sync_results.json`
- `sync_report.md`
- `sync_confidence.csv`
- `manual_sync_review.csv`

Purpose:

- record possible video/audio matches;
- store selected sync decisions;
- preserve method and confidence;
- expose offsets and drift warnings;
- mark uncertain results for human review.

An uncertain sync must not be marked as final.

## 03_transcripts_original

The `03_transcripts_original/` folder stores original-language transcript outputs.

Required files:

- `transcripts_original.json`
- `transcript_warnings.json`
- `manual_transcript_review.csv`

Optional generated files:

- `clip_001_original.en.txt`
- `clip_001_original.en.srt`
- `clip_002_original.fr.txt`
- `clip_002_original.fr.srt`
- `clip_003_original.ar.txt`
- `clip_003_original.ar.srt`

Purpose:

- preserve original dialogue;
- keep original-language transcripts separate from translations;
- keep timestamps available for editorial review;
- mark uncertain language or transcription segments.

The original transcript must be preserved separately from translations.

## 04_subtitles_spanish

The `04_subtitles_spanish/` folder stores Spanish translated working subtitles.

Required files:

- `subtitles_es_working.json`
- `subtitle_translation_warnings.json`
- `manual_subtitle_review.csv`

Optional generated files:

- `clip_001_es_trabajo.srt`
- `clip_002_es_trabajo.srt`
- `clip_003_es_trabajo.srt`
- `timeline_subtitles_es_trabajo.srt`
- `bilingual_original_plus_es_review.srt`

Purpose:

- provide Spanish translated working subtitles;
- preserve link to original transcript segment;
- make translations reviewable;
- prepare Spanish SRT files for DaVinci Resolve.

Spanish translated subtitles must use target language `es`.

Automatically generated Spanish subtitles are working subtitles unless human validated.

## 05_editorial_summary

The `05_editorial_summary/` folder stores editorial analysis outputs.

Required files:

- `editorial_selects.json`
- `resumen_general.md`
- `mejores_momentos.md`
- `clips_revisar.md`
- `translator_review.md`
- `technical_review.md`

Purpose:

- summarize useful moments;
- group selects for rough cut;
- mark language and subtitle needs;
- identify clips useful for teaser or story context;
- identify clips needing human review.

Editorial summaries are local artifacts unless explicitly authorized for connected mode.

## 06_davinci

The `06_davinci/` folder stores DaVinci Resolve rough-cut assist outputs.

Required files:

- `rough_cut_selects.otio`
- `rough_cut_markers.csv`
- `timeline_subtitles_es.srt`
- `import_instructions.md`
- `davinci_package_manifest.json`

Optional files:

- `rough_cut_selects.edl`
- `rough_cut_selects.fcpxml`

Purpose:

- prepare a DaVinci Resolve-friendly package;
- expose selects timeline data;
- provide Spanish subtitle files;
- provide marker files;
- provide human-readable import instructions.

The DaVinci package is a rough-cut assist, not a final automatic edit.

## 90_temp

The `90_temp/` folder stores temporary local processing files.

Allowed subfolders:

- `audio_analysis/`
- `waveform_cache/`
- `transcription_cache/`
- `subtitle_cache/`
- `ffprobe_cache/`

Purpose:

- store local temporary files needed for analysis;
- avoid writing temporary files beside original media;
- make cleanup predictable.

Temporary files must remain local.

Temporary files must not be uploaded.

The app must support a safe cleanup mode for `90_temp/`.

## 99_logs

The `99_logs/` folder stores local operational logs.

Required files:

- `processing_log.md`
- `errors.json`
- `warnings.json`
- `license_events.json`
- `privacy_events.json`

Purpose:

- record local execution state;
- log errors and warnings;
- record license checks without exposing client media;
- record privacy-sensitive decisions;
- support support/debug workflows without copying media.

Logs must avoid full local paths by default in connected reports.

Logs must not include video frames, audio payloads, transcripts, subtitles, or editorial summaries unless explicitly allowed in a future support mode.

## Human review index

Human review must be represented explicitly.

The output root must provide review files for:

- scan review;
- sync review;
- transcript review;
- translation review;
- subtitle review;
- editorial select review;
- DaVinci export review.

Human review files must not be removed to make the product appear more automatic than it is.

## File naming rules

Generated files must use predictable names.

Rules:

- use lowercase descriptive names for system files;
- use `_es_trabajo` for Spanish working subtitles;
- use `_original.<language>` for original-language transcript or subtitle files;
- use `.json` for machine-readable outputs;
- use `.md` for human-readable reports;
- use `.csv` for review tables;
- use `.srt` for subtitle files;
- use `.otio`, `.edl`, or `.fcpxml` only for editorial interchange outputs.

## Safety requirements

The app must not:

- copy original video files into `CID_OUTPUT/`;
- copy original audio files into `CID_OUTPUT/`;
- rewrite original camera media;
- rewrite original sound media;
- delete original media;
- rename original media;
- upload generated files without explicit authorization;
- send full local paths to CID SaaS without explicit permission;
- mark working subtitles as final without human validation;
- mark rough-cut assist as final edit.

## Acceptance criteria

This phase is accepted when:

- the output root is documented;
- all required top-level folders are documented;
- required files for each folder are documented;
- local-only privacy is preserved;
- original media copying is forbidden;
- temporary files are constrained to `90_temp/`;
- logs are constrained to `99_logs/`;
- Spanish working subtitle outputs are defined;
- DaVinci rough-cut assist outputs are defined;
- human review files are required;
- explicit non-goals protect CID SaaS from accidental integration work.

## Non-goals of this phase

This phase does not implement filesystem creation, file writing, cleanup, scanner logic, ffprobe calls, ffmpeg calls, waveform sync, transcription, translation, subtitle generation, DaVinci export, CLI commands, GUI code, licensing, iLok/PACE, SaaS runtime, backend routes, database models, Alembic, Docker, frontend, Stripe, AI Jobs, credits, ledger, workers, or production configuration.
